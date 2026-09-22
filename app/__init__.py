import os
import uuid
import logging

from pythonjsonlogger import jsonlogger

from flask import Flask, g, request
from prometheus_flask_exporter import PrometheusMetrics

from app.config import Config
from app.extensions import db, migrate, jwt

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# -----------------------------
# Rate Limiter
# -----------------------------
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
)


def create_app():

    app = Flask(__name__)

    # -----------------------------
    # Configuration
    # -----------------------------
    app.config.from_object(Config)

    # -----------------------------
    # JSON Structured Logging
    # -----------------------------
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_handler = logging.StreamHandler()

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(message)s"
    )

    log_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(log_handler)

    # -----------------------------
    # Prometheus Metrics
    # -----------------------------
    metrics = PrometheusMetrics(app)

    # -----------------------------
    # Correlation ID
    # -----------------------------
    @app.before_request
    def add_correlation_id():
        g.correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4())
        )

    @app.after_request
    def add_correlation_header(response):
        response.headers["X-Correlation-ID"] = g.correlation_id

        print("CORRELATION ID:", g.correlation_id)

        return response

    # -----------------------------
    # Initialize Extensions
    # -----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # -----------------------------
    # Initialize Rate Limiter
    # -----------------------------
    limiter.init_app(app)

    # -----------------------------
    # Import Models
    # -----------------------------
    from app.auth.models import User
    from app.catalog.models import Product
    from app.orders.models import Order, OrderItem

    # -----------------------------
    # Import Routes
    # -----------------------------
    from app.auth.routes import auth_bp
    from app.catalog.routes import catalog_bp
    from app.orders.routes import orders_bp

    # -----------------------------
    # Register Blueprints
    # -----------------------------
    app.register_blueprint(
        auth_bp,
        url_prefix="/auth"
    )

    app.register_blueprint(
        catalog_bp,
        url_prefix="/catalog"
    )

    app.register_blueprint(
        orders_bp,
        url_prefix="/orders"
    )

    # -----------------------------
    # Home Route
    # -----------------------------
    @app.route("/")
    def home():
        return {
            "message": "E-Commerce API is running"
        }

    return app