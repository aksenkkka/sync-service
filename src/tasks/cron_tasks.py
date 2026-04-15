import asyncio

from celery import shared_task

from src.config import settings
from src.interfaces.contacts import ContactsInterface
from src.repositories.contacts import ContactsRepository


@shared_task
def sync_contacts():
    async def _run():
        await ContactsRepository.connect(settings.POSTGRESDB_URL)
        await ContactsInterface.sync_contacts()

    asyncio.run(_run())