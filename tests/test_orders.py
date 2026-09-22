import pytest

from app import create_app
from app.extensions import db
from app.auth.models import User
from werkzeug.security import generate_password_hash


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


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            name="Order Test User",
            email="ordertest@example.com",
            password_hash=generate_password_hash("TestPassword123!"),
            role="customer"
        )

        db.session.add(user)
        db.session.commit()

        user_id = user.id

    return user_id


def test_orders_test_endpoint(client):
    response = client.get("/orders/test")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Orders module is working"


def test_create_order_requires_data(client):
    response = client.post(
        "/orders/",
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "user_id and total_amount are required"


def test_create_order_user_not_found(client):
    response = client.post(
        "/orders/",
        json={
            "user_id": 999999,
            "total_amount": 5000
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "User not found"


def test_create_order(client, test_user, monkeypatch):
    # Prevent actual Celery tasks from running
    class MockTask:
        @staticmethod
        def delay(*args, **kwargs):
            return None

    monkeypatch.setattr(
        "app.orders.routes.generate_invoice_pdf",
        MockTask()
    )

    monkeypatch.setattr(
        "app.orders.routes.send_email_task",
        MockTask()
    )

    response = client.post(
        "/orders/",
        json={
            "user_id": test_user,
            "total_amount": 5000
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Order created successfully"
    assert data["order_id"] is not None
    assert data["customer_email"] == "ordertest@example.com"
    assert data["invoice"].startswith("invoice_")
    assert data["email"] == "Confirmation email queued"