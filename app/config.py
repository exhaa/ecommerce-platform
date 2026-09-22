import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:

    # Rate limiting storage
    RATELIMIT_STORAGE_URI = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # Flask secret
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-development-secret"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "change-this-jwt-development-secret"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # RabbitMQ
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")

    # Request size limit: 10 MB
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024