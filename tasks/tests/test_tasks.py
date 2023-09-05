import unittest.mock

import pytest

from tasks.constants import SystemRole
from tasks.models import Task, User
from tasks.tests.conftest import sign_in
from tasks.tests.helpers import TOMORROW


class TestTasksBase:
    @pytest.fixture
    def setup(self):
        self.admin = User.objects.create_superuser(email="admin@mail.com", password="admin@35762!")
        self.operator = User.objects.create_user(
            email="operator@mail.com", password="operator@35762!", roles=[SystemRole.OPERATOR]
        )
        self.manager = User.objects.create_user(
            email="manager@mail.com", password="manager@35762!", roles=[SystemRole.MANAGER]
        )
        self.task1 = Task.objects.create(
            title="task 1",
            description="description 1",
            due_date=TOMORROW,
            created_by=self.admin,
        )
        self.task2 = Task.objects.create(
            title="task 2", description="description 2", status="P", created_by=self.operator
        )
        self.task3 = Task.objects.create(
            title="task 3",
            description="description 3",
            created_by=self.manager,
            assigned_to=self.operator,
        )
        self.ROLE_TO_USER_DATA = {
            SystemRole.ADMIN: (self.admin.email, "admin@35762!"),
            SystemRole.OPERATOR: (self.operator.email, "operator@35762!"),
            SystemRole.MANAGER: (self.manager.email, "manager@35762!"),
        }


@pytest.mark.django_db
class TestTasks(TestTasksBase):
    @pytest.mark.parametrize(
        "role, task_quantity",
        [
            (SystemRole.ADMIN, 3),
            (SystemRole.OPERATOR, 2),
            (SystemRole.MANAGER, 1),
        ],
    )
    def test_get_list(self, setup, api_client, role, task_quantity):
        email, password = self.ROLE_TO_USER_DATA.get(role)
        token = sign_in(api_client, email, password)
        response = api_client.get("/api/tasks/", headers={"Authorization": f"Bearer {token}"})
        resp_data = response.json()

        assert len(resp_data) == task_quantity

    @pytest.mark.parametrize(
        "params, task_quantity",
        [
            ({"status": "N"}, 2),
            ({"due_date": TOMORROW}, 1),
            ({"title": "TASK 3"}, 1),
        ],
    )
    def test_filters(self, setup, api_client, params, task_quantity):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.ADMIN)
        token = sign_in(api_client, email, password)
        response = api_client.get(
            "/api/tasks/", data=params, headers={"Authorization": f"Bearer {token}"}
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert len(resp_data) == task_quantity

    def test_get(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.ADMIN)
        token = sign_in(api_client, email, password)
        response = api_client.get(
            f"/api/tasks/{self.task2.id}/", headers={"Authorization": f"Bearer {token}"}
        )
        resp_data = response.json()

        assert resp_data["id"] == self.task2.id
        assert resp_data["title"] == self.task2.title

    def test_create(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.OPERATOR)
        token = sign_in(api_client, email, password)

        task_data = {
            "title": "new task",
            "description": "new task desc",
            "status": "P",
            "assigned_to": self.manager.id,
        }
        response = api_client.post(
            "/api/tasks/",
            data=task_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_data = response.json()

        assert resp_data["title"] == task_data["title"]
        assert resp_data["description"] == task_data["description"]
        assert resp_data["status"] == task_data["status"]
        assert resp_data["assigned_to"] == task_data["assigned_to"]

    @unittest.mock.patch("tasks.views.tasks.celery_send_email.delay")
    def test_update(self, mock_send_email, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.OPERATOR)
        token = sign_in(api_client, email, password)

        update_data = {
            "title": "new title",
            "description": "updated desc",
            "status": "C",
            "assigned_to": self.manager.id,
        }
        response = api_client.post(
            f"/api/tasks/{self.task2.id}/",
            data=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_data = response.json()

        mock_send_email.assert_called_once()
        assert resp_data["title"] == update_data["title"]
        assert resp_data["description"] == update_data["description"]
        assert resp_data["status"] == update_data["status"]
        assert resp_data["assigned_to"] == update_data["assigned_to"]


@pytest.mark.django_db
class TestTasksPermissions(TestTasksBase):
    def test_get_assigned_owned_tasks(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.OPERATOR)
        token = sign_in(api_client, email, password)
        response = api_client.get("/api/tasks/", headers={"Authorization": f"Bearer {token}"})
        resp_data = response.json()

        own_created_task = next(
            task for task in resp_data if task["created_by"] == self.operator.id
        )
        assigned_task = next(task for task in resp_data if task["assigned_to"] == self.operator.id)
        assert len(resp_data) == 2
        assert own_created_task["id"] == self.task2.id
        assert assigned_task["id"] == self.task3.id

    def test_get_all_tasks_by_admin(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.ADMIN)
        token = sign_in(api_client, email, password)
        response = api_client.get("/api/tasks/", headers={"Authorization": f"Bearer {token}"})
        resp_data = response.json()

        assert len(resp_data) == 3

    def test_get_not_owned_task_by_id(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.OPERATOR)
        token = sign_in(api_client, email, password)

        response = api_client.get(
            f"/api/tasks/{self.task1.id}/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_get_any_task_by_admin(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.ADMIN)
        token = sign_in(api_client, email, password)

        response = api_client.get(
            f"/api/tasks/{self.task3.id}/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        resp_data = response.json()
        assert resp_data["id"] == self.task3.id

    def test_update_not_owned_task(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.OPERATOR)
        token = sign_in(api_client, email, password)

        response = api_client.post(
            f"/api/tasks/{self.task1.id}/",
            data={"status": "I"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    @unittest.mock.patch("tasks.views.tasks.celery_send_email.delay")
    def test_update_any_task_by_admin(self, mock_send_email, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.ADMIN)
        token = sign_in(api_client, email, password)

        response = api_client.post(
            f"/api/tasks/{self.task3.id}/",
            data={"status": "I"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        resp_data = response.json()
        assert resp_data["status"] == "I"
        mock_send_email.assert_not_called()

    def test_delete_owned_task(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.OPERATOR)
        token = sign_in(api_client, email, password)

        response = api_client.delete(
            f"/api/tasks/{self.task2.id}/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        deleted = Task.objects.filter(id=self.task2.id).first()
        assert not deleted

    def test_delete_not_owned_task(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.OPERATOR)
        token = sign_in(api_client, email, password)

        response = api_client.delete(
            f"/api/tasks/{self.task1.id}/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        actual_task = Task.objects.filter(id=self.task1.id).first()
        assert actual_task

    def test_delete_any_task_by_admin(self, setup, api_client):
        email, password = self.ROLE_TO_USER_DATA.get(SystemRole.ADMIN)
        token = sign_in(api_client, email, password)

        response = api_client.delete(
            f"/api/tasks/{self.task3.id}/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        deleted = Task.objects.filter(id=self.task3.id).first()
        assert not deleted
