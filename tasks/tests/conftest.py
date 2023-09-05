import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


def sign_in(api_client, email: str, password: str) -> str:
    auth_response = api_client.post("/api/token/", data={"email": email, "password": password})
    token_data = auth_response.json()
    return token_data["access"]
