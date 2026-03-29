from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_user_payload(prefix: str = "user") -> dict:
    unique = uuid4().hex[:8]
    return {
        "username": f"{prefix}_{unique}",
        "email": f"{prefix}_{unique}@example.com",
        "password": "secret123",
    }


def test_register_user() -> None:
    payload = unique_user_payload("testuser")

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "hashed_password" not in data


def test_login_user() -> None:
    register_payload = unique_user_payload("loginuser")

    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": register_payload["email"],
            "password": register_payload["password"],
        },
    )

    assert login_response.status_code == 200, login_response.text
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_protected_route_with_valid_token() -> None:
    register_payload = unique_user_payload("protecteduser")

    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": register_payload["email"],
            "password": register_payload["password"],
        },
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/protected-health",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert register_payload["email"] in data["message"]


def test_protected_route_with_invalid_token() -> None:
    response = client.get(
        "/api/v1/protected-health",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Could not validate credentials"