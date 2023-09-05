import pytest

from tasks.constants import SystemRole
from tasks.models import Role, User
from tasks.tests.conftest import sign_in


class TestUsersBase:
    @pytest.fixture
    def setup(self):
        self.admin = User.objects.create_superuser(email="admin@mail.com", password="admin@35762!")
        self.operator = User.objects.create_user(
            email="operator@mail.com",
            is_active=False,
            password="operator@35762!",
            roles=[SystemRole.OPERATOR],
        )
        self.manager = User.objects.create_user(
            email="manager@mail.com", password="manager@35762!", roles=[SystemRole.MANAGER]
        )

        self.admin_email = "admin@mail.com"
        self.admin_password = "admin@35762!"
        self.operator_email = "operator@mail.com"
        self.operator_password = "operator@35762!"
        self.manager_email = "manager@mail.com"
        self.manager_password = "manager@35762!"


@pytest.mark.django_db
class TestUsersAdmin(TestUsersBase):
    def test_get_list(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
        resp_data = response.json()

        assert response.status_code == 200
        assert len(resp_data) == 2

    def test_get(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.get(
            f"/api/users/{self.manager.id}/", headers={"Authorization": f"Bearer {token}"}
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert resp_data["id"] == self.manager.id

    def test_get_not_active(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.get(
            f"/api/users/{self.operator.id}/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_create(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.post(
            "/api/users/",
            data={
                "email": "new@mail.com",
                "password": "Newp@ss123",
                "first_name": "John",
                "last_name": "Doe",
                "roles": [SystemRole.MANAGER],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_data = response.json()

        assert response.status_code == 201
        assert resp_data["first_name"] == "John"
        assert resp_data["last_name"] == "Doe"

    def test_email_uniqueness(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.post(
            "/api/users/",
            data={
                "email": self.admin.email,
                "password": "Newp@ss123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    def test_update(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.post(
            f"/api/users/{self.manager.id}/",
            data={
                "first_name": "Test",
                "last_name": "User",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert resp_data["first_name"] == "Test"
        assert resp_data["last_name"] == "User"

    def test_update_roles(self, setup, api_client):
        admin_role = Role.objects.get(name=SystemRole.ADMIN)
        operator_role = Role.objects.get(name=SystemRole.OPERATOR)
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.post(
            f"/api/users/{self.manager.id}/",
            data={
                "roles": [admin_role.id, operator_role.id],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert len(resp_data["roles"]) == 2

    def test_delete(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.delete(
            f"/api/users/{self.manager.id}/", headers={"Authorization": f"Bearer {token}"}
        )
        resp_data = response.json()
        manager = User.objects.get(id=self.manager.id)

        assert response.status_code == 200
        assert not resp_data["is_active"]
        assert not manager.is_active


@pytest.mark.django_db
class TestUsersNoAdmin(TestUsersBase):
    def test_get(self, setup, api_client):
        token = sign_in(api_client, self.manager_email, self.manager_password)
        response = api_client.get(
            f"/api/users/{self.manager.id}/", headers={"Authorization": f"Bearer {token}"}
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert resp_data["id"] == self.manager.id

    def test_get_another_user(self, setup, api_client):
        token = sign_in(api_client, self.manager_email, self.manager_password)
        response = api_client.get(
            f"/api/users/{self.admin.id}/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

    def test_create(self, setup, api_client):
        token = sign_in(api_client, self.manager_email, self.manager_password)
        response = api_client.post(
            "/api/users/",
            data={
                "email": "new@mail.com",
                "password": "Newp@ss123",
                "first_name": "John",
                "last_name": "Doe",
                "roles": [SystemRole.MANAGER],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_update(self, setup, api_client):
        token = sign_in(api_client, self.manager_email, self.manager_password)
        response = api_client.post(
            f"/api/users/{self.manager.id}/",
            data={
                "email": "new@mail.com",
                "password": "Newp@ss123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert resp_data["email"] == "new@mail.com"

    def test_update_another_user(self, setup, api_client):
        token = sign_in(api_client, self.manager_email, self.manager_password)
        response = api_client.post(
            f"/api/users/{self.admin.id}/",
            data={"first_name": "admin"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_add_role_not_changed(self, setup, api_client):
        admin_role = Role.objects.get(name=SystemRole.ADMIN)
        token = sign_in(api_client, self.manager_email, self.manager_password)
        response = api_client.post(
            f"/api/users/{self.manager.id}/",
            data={"roles": [admin_role.id]},
            headers={"Authorization": f"Bearer {token}"},
        )
        manager_role = Role.objects.get(name=SystemRole.MANAGER)
        updated_manager = User.objects.get(id=self.manager.id)

        assert response.status_code == 200
        assert list(updated_manager.roles.all()) == [manager_role]

    def test_delete(self, setup, api_client):
        token = sign_in(api_client, self.manager_email, self.manager_password)
        response = api_client.delete(
            f"/api/users/{self.manager.id}/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
