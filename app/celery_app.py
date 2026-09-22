import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()


def create_celery():
    celery = Celery(
        "ecommerce",
        broker=os.getenv(
            "RABBITMQ_URL",
            "amqp://guest:guest@localhost:5672//"
        ),
        backend=os.getenv(
            "REDIS_URL",
            "redis://localhost:6379/0"
        ),
        include=[
            "app.tasks.test_tasks",
            "app.tasks.email_tasks",
            "app.tasks.pdf_tasks",
            "app.tasks.dlq_tasks",
        ]
    )

    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )

    return celery


celery = create_celery()