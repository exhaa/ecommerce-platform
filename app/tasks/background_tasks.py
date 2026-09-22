from app.celery_app import celery


@celery.task
def background_task(name):
    print(f"Background task executed for {name}")
    return f"Hello {name}"