from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.auth.models import User
from app.auth.schemas import RegisterSchema
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import check_password_hash
from app.extensions import limiter
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/test", methods=["GET"])
def auth_test():
    return jsonify({
        "message": "Auth module is working"
    })


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate request data
        validated_data = RegisterSchema.model_validate(data)

    except ValidationError as error:
        return jsonify({
            "error": "Validation failed",
            "details": error.errors()
        }), 400

    # Check if email already exists
    existing_user = User.query.filter_by(
        email=validated_data.email
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email already exists"
        }), 409

    # Hash password before saving
    hashed_password = generate_password_hash(
        validated_data.password
    )

    # Create user
    new_user = User(
        name=validated_data.name,
        email=str(validated_data.email),
        password_hash=hashed_password,
        role="customer"
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not check_password_hash(
        user.password_hash,
        password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }), 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()

    new_access_token = create_access_token(
        identity=user_id
    )

    return jsonify({
        "access_token": new_access_token
    }), 200