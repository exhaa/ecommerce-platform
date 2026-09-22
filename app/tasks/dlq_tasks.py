from app.celery_app import celery
from pathlib import Path
from datetime import datetime


@celery.task
def save_failed_task(task_name, task_args, error_message):

    dlq_dir = Path("dead_letter_queue")
    dlq_dir.mkdir(exist_ok=True)

    file_path = dlq_dir / "failed_tasks.txt"

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(
            f"Time: {datetime.now()}\n"
            f"Task: {task_name}\n"
            f"Arguments: {task_args}\n"
            f"Error: {error_message}\n"
            f"{'-' * 50}\n"
        )

    print(f"Failed task saved to DLQ: {file_path}")

    return str(file_path)