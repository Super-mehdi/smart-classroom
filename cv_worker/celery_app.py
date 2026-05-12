import os
from celery import Celery
from dotenv import load_dotenv
 
load_dotenv()
 
celery_app = Celery(
    "cv_worker",
    broker=os.environ["CELERY_BROKER"],
    backend=os.environ.get("CELERY_RESULT_BACKEND", os.environ["CELERY_BROKER"].replace("/1", "/2")),
    include=["tasks"],
)
 
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "post-attention-every-5s": {
            "task": "tasks.post_attention_batch",
            "schedule": 5.0,
        },
    },
)
