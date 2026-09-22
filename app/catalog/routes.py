from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.extensions import db
from app.catalog.models import Product
from app.catalog.schemas import ProductSchema
import json
from app.catalog.cache import invalidate_product_cache
from app.redis_client import redis_client

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/test", methods=["GET"])
def catalog_test():
    return jsonify({
        "message": "Catalog module is working"
    })


@catalog_bp.route("/products", methods=["POST"])
def create_product():
    try:
        # Get JSON data
        data = request.get_json()

        # Validate product data
        validated_data = ProductSchema.model_validate(data)

    except ValidationError as error:
        return jsonify({
            "error": "Validation failed",
            "details": error.errors()
        }), 400

    # Create product
    new_product = Product(
        name=validated_data.name,
        description=validated_data.description,
        price=validated_data.price,
        stock=validated_data.stock
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "description": new_product.description,
            "price": str(new_product.price),
            "stock": new_product.stock
        }
    }), 201

@catalog_bp.route("/products", methods=["GET"])
def get_products():

    cache_key = "catalog:products"

    # Check Redis first
    cached_products = redis_client.get(cache_key)

    if cached_products:
        return jsonify({
            "source": "cache",
            "products": json.loads(cached_products)
        }), 200

    # Get products from database
    products = Product.query.all()

    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
            "stock": product.stock
        }
        for product in products
    ]

    # Store in Redis for 60 seconds
    redis_client.setex(
        cache_key,
        60,
        json.dumps(product_list)
    )

    return jsonify({
        "source": "database",
        "products": product_list
    }), 200

@catalog_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    try:
        # Get JSON data
        data = request.get_json()

        # Validate updated product data
        validated_data = ProductSchema.model_validate(data)

    except ValidationError as error:
        return jsonify({
            "error": "Validation failed",
            "details": error.errors()
        }), 400

    # Update product
    product.name = validated_data.name
    product.description = validated_data.description
    product.price = validated_data.price
    product.stock = validated_data.stock

    # Save changes to PostgreSQL
    db.session.commit()

    # Invalidate Redis cache
    invalidate_product_cache()

    return jsonify({
        "message": "Product updated successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
            "stock": product.stock
        }
    }), 200