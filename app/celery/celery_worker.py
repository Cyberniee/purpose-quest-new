from celery import Celery
import os

celery_app = Celery(
    "report_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

celery_app.conf.task_routes = {
    "app.modules.tasks.report_generation.generate_report_chapter": {"queue": "reports"},
}
