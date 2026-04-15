import asyncio

from celery import Celery
from celery.schedules import schedule
from celery.signals import worker_process_init
from kombu import Queue

from src.config import settings
from src.repositories.contacts import ContactsRepository

celery = Celery(
    __name__, broker="redis://redis:6379/0", include=["src.tasks.cron_tasks"]
)

celery.conf.timezone = "Europe/Kyiv"


celery.conf.beat_schedule = {
    "sync_contacts_every_30_seconds": {
        "task": "src.tasks.cron_tasks.sync_contacts",
        "schedule": schedule(run_every=30.0),  # every 30 seconds
        "args": (),
    },
}


@worker_process_init.connect
def init_db(**kwargs):
    asyncio.run(ContactsRepository.connect(settings.POSTGRESDB_URL))


celery.conf.task_queues = (Queue("default", routing_key="default"),)

celery.conf.task_default_queue = "default"


celery.conf.worker_send_task_events = True
celery.conf.worker_track_started = True
celery.conf.task_acks_late = True
celery.conf.worker_disable_rate_limits = True