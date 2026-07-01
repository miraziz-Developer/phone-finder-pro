from fastapi.testclient import TestClient

from app.presentation.api.app import create_api_app


def test_health_endpoint() -> None:
    client = TestClient(create_api_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_returns_token() -> None:
    client = TestClient(create_api_app())
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin_secret_change_me"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 10
