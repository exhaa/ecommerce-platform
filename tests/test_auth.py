import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_auth_test_endpoint(client):
    response = client.get("/auth/test")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Auth module is working"


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "testauth@example.com",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "User registered successfully"
    assert data["user"]["email"] == "testauth@example.com"
    assert data["user"]["role"] == "customer"


def test_duplicate_email(client):
    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPassword123!"
    }

    first_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json=user_data
    )

    assert second_response.status_code == 409
    assert second_response.get_json()["error"] == "Email already exists"


def test_login(client):
    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "TestPassword123!"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Login successful"
    assert "access_token" in data
    assert "refresh_token" in data


def test_me_requires_login(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_login(client):
    client.post(
        "/auth/register",
        json={
            "name": "Me User",
            "email": "me@example.com",
            "password": "TestPassword123!"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "TestPassword123!"
        }
    )

    access_token = login_response.get_json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["email"] == "me@example.com"
    assert data["name"] == "Me User"
    assert data["role"] == "customer"