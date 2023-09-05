import pytest

from tasks.constants import SystemRole
from tasks.models import User


@pytest.mark.django_db
class TestTokens:
    @pytest.fixture
    def setup(self):
        self.admin = User.objects.create_superuser(email="admin@mail.com", password="admin@35762!")
        self.operator = User.objects.create_user(
            email="operator@mail.com",
            is_active=False,
            password="operator@35762!",
            roles=[SystemRole.OPERATOR],
        )
        self.admin_email = "admin@mail.com"
        self.admin_password = "admin@35762!"
        self.operator_email = "operator@mail.com"
        self.operator_password = "operator@35762!"

    def test_get_token_pair(self, setup, api_client):
        response = api_client.post(
            "/api/token/", data={"email": self.admin_email, "password": self.admin_password}
        )
        token_data = response.json()

        assert response.status_code == 200
        assert token_data.get("access")
        assert token_data.get("refresh")

    def test_refresh_token_pair(self, setup, api_client):
        response = api_client.post(
            "/api/token/", data={"email": self.admin_email, "password": self.admin_password}
        )
        token_data = response.json()

        response = api_client.post(
            "/api/token/refresh/",
            data={
                "refresh": token_data["refresh"],
            },
        )
        resp_data = response.json()

        assert response.status_code == 200
        assert resp_data["access"] != token_data["access"]

    def test_get_for_non_active_user(self, setup, api_client):
        response = api_client.post(
            "/api/token/", data={"email": self.operator_email, "password": self.operator_password}
        )
        assert response.status_code == 401
