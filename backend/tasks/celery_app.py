import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "backend",
    broker=os.environ["CELERY_BROKER"],
    backend=os.environ["CELERY_RESULT_BACKEND"],
    include=[
        "tasks.email_tasks",
        "tasks.alert_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_ignore_result=True,
    task_default_queue="backend",    # ← separate queue
    beat_schedule={
        "check-alert-thresholds": {
            "task": "tasks.alert_tasks.check_thresholds",
            "schedule": 30.0,
            "options": {"queue": "backend"},
        },
    },
)