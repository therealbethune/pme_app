"""
Celery application configuration for PME Calculator background tasks.
"""

from celery import Celery

# Create Celery instance with Redis broker and backend
celery = Celery(
    "pme", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
)

# Configure Celery settings
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    task_routes={
        "worker.tasks.run_metrics": {"queue": "analytics"},
        "worker.tasks.generate_pdf_report": {"queue": "reports"},
    },
)

# Auto-discover tasks
celery.autodiscover_tasks(["worker"])
