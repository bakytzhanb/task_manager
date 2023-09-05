import pytest

from tasks.constants import SystemRole
from tasks.models import Role, User
from tasks.tests.conftest import sign_in


@pytest.mark.django_db
class TestRoles:
    @pytest.fixture
    def setup(self):
        User.objects.create_superuser(email="admin@mail.com", password="admin@35762!")
        User.objects.create_user(
            email="operator@mail.com", password="operator@35762!", roles=[SystemRole.OPERATOR]
        )
        self.admin_role = Role.objects.get(name=SystemRole.ADMIN)
        self.admin_email = "admin@mail.com"
        self.admin_password = "admin@35762!"
        self.operator_email = "operator@mail.com"
        self.operator_password = "operator@35762!"

    def test_get_list(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.get("/api/roles/", headers={"Authorization": f"Bearer {token}"})
        resp_data = response.json()

        assert response.status_code == 200
        assert len(resp_data) == 3

    def test_get(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.get(
            f"/api/roles/{self.admin_role.id}/", headers={"Authorization": f"Bearer {token}"}
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert resp_data["id"] == self.admin_role.id
        assert resp_data["name"] == SystemRole.ADMIN

    def test_create(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.post(
            "/api/roles/", data={"name": "developer"}, headers={"Authorization": f"Bearer {token}"}
        )
        resp_data = response.json()

        assert response.status_code == 201
        assert resp_data["name"] == "developer"

    def test_update(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.post(
            f"/api/roles/{self.admin_role.id}/",
            data={"name": "new_role"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert resp_data["name"] == "new_role"

    def test_delete(self, setup, api_client):
        token = sign_in(api_client, self.admin_email, self.admin_password)
        response = api_client.delete(
            f"/api/roles/{self.admin_role.id}/", headers={"Authorization": f"Bearer {token}"}
        )

        deleted = Role.objects.filter(id=self.admin_role.id).first()
        assert response.status_code == 200
        assert not deleted

    def test_get_non_admin_403(self, setup, api_client):
        token = sign_in(api_client, self.operator_email, self.operator_password)
        response = api_client.get(
            f"/api/roles/{self.admin_role.id}/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

    def test_update_non_admin_403(self, setup, api_client):
        token = sign_in(api_client, self.operator_email, self.operator_password)
        response = api_client.post(
            f"/api/roles/{self.admin_role.id}/",
            data={"name": "new_role"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_delete_non_admin_403(self, setup, api_client):
        token = sign_in(api_client, self.operator_email, self.operator_password)
        response = api_client.delete(
            f"/api/roles/{self.admin_role.id}/", headers={"Authorization": f"Bearer {token}"}
        )

        not_deleted = Role.objects.filter(id=self.admin_role.id).first()
        assert response.status_code == 403
        assert not_deleted
