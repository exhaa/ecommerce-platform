import pytest

from app import create_app
from app.extensions import db
from app.redis_client import redis_client


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    # Clear catalog cache before tests
    try:
        redis_client.delete("catalog:products")
    except Exception:
        pass

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

    try:
        redis_client.delete("catalog:products")
    except Exception:
        pass


@pytest.fixture
def client(app):
    return app.test_client()


def test_catalog_test_endpoint(client):
    response = client.get("/catalog/test")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Catalog module is working"


def test_create_product(client):
    response = client.post(
        "/catalog/products",
        json={
            "name": "Test Laptop",
            "description": "Test product",
            "price": 150000,
            "stock": 10
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Product created successfully"
    assert data["product"]["name"] == "Test Laptop"
    assert data["product"]["stock"] == 10


def test_get_products(client):
    client.post(
        "/catalog/products",
        json={
            "name": "Test Phone",
            "description": "Test phone",
            "price": 50000,
            "stock": 20
        }
    )

    response = client.get("/catalog/products")

    assert response.status_code == 200

    data = response.get_json()

    assert "products" in data
    assert len(data["products"]) == 1
    assert data["products"][0]["name"] == "Test Phone"


def test_get_products_uses_cache(client):
    client.post(
        "/catalog/products",
        json={
            "name": "Cached Product",
            "description": "Testing Redis cache",
            "price": 1000,
            "stock": 5
        }
    )

    # First request loads the database and stores data in Redis
    first_response = client.get("/catalog/products")

    assert first_response.status_code == 200

    # Second request should use Redis cache
    second_response = client.get("/catalog/products")

    assert second_response.status_code == 200

    data = second_response.get_json()

    assert data["source"] == "cache"
    assert len(data["products"]) == 1


def test_update_product(client):
    create_response = client.post(
        "/catalog/products",
        json={
            "name": "Old Product",
            "description": "Old description",
            "price": 1000,
            "stock": 5
        }
    )

    product_id = create_response.get_json()["product"]["id"]

    update_response = client.put(
        f"/catalog/products/{product_id}",
        json={
            "name": "Updated Product",
            "description": "Updated description",
            "price": 2000,
            "stock": 10
        }
    )

    assert update_response.status_code == 200

    data = update_response.get_json()

    assert data["message"] == "Product updated successfully"
    assert data["product"]["name"] == "Updated Product"
    assert data["product"]["stock"] == 10


def test_update_nonexistent_product(client):
    response = client.put(
        "/catalog/products/999999",
        json={
            "name": "Unknown",
            "description": "Unknown product",
            "price": 1000,
            "stock": 5
        }
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"