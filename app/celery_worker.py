from celery import Celery
import os

celery_app = Celery(
    "report_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"),
)

celery_app.autodiscover_tasks([
    "app.modules.tasks",
])

from app.modules.tasks import report_generation
