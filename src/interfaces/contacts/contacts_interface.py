from typing import List, Optional

import httpx

from src.models.contacts import ContactModel
from src.repositories.contacts.contacts_repository import ContactsRepository


class ContactsInterface:
    repository = ContactsRepository
    model = ContactModel

    API_TOKEN = "NxkA2RlXS3NiR8SKwRdDmroA992jgu"
    BASE_URL = "https://app.nimble.com/api/v1/contacts"

    @classmethod
    async def search_contacts(
        cls, query: str, limit: int = 10, offset: int = 0
    ) -> List[ContactModel]:
        """
        Perform full-text search for contacts in the database.
        """
        if not ContactsRepository._conn:
            raise RuntimeError("Database connection not initialized")

        sql = """
        SELECT first_name, last_name, email, description
        FROM contacts
        WHERE to_tsvector('english', coalesce(first_name,'') || ' ' || coalesce(last_name,'') || ' ' || coalesce(description,''))
              @@ plainto_tsquery('english', $1)
        ORDER BY ts_rank_cd(
            to_tsvector('english', coalesce(first_name,'') || ' ' || coalesce(last_name,'') || ' ' || coalesce(description,'')),
            plainto_tsquery('english', $1)
        ) DESC
        LIMIT $2 OFFSET $3
        """
        rows = await ContactsRepository.fetch(sql, query, limit, offset)

        return [ContactModel(**row) for row in rows]

    @classmethod
    async def sync_contacts(cls):
        """
        Sync fetched contacts with database
        """
        contacts = await cls.fetch_contacts_from_api()
        for contact in contacts:
            await ContactsRepository.upsert_contact(
                email=contact.email,
                first_name=contact.first_name,
                last_name=contact.last_name,
                description=contact.description,
            )

    @classmethod
    async def fetch_contacts_from_api(cls) -> List[ContactModel]:
        """
        Perform syncing contacts with external API
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                cls.BASE_URL,
                headers={"Authorization": f"Bearer {cls.API_TOKEN}"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        contacts: List[ContactModel] = []

        for resource in data.get("resources", []):
            fields = resource.get("fields", {})

            first_name = cls._extract_field(fields, "first name")
            last_name = cls._extract_field(fields, "last name")

            email = cls._extract_field(fields, "email")
            if not email:
                continue

            description = cls._extract_field(fields, "description")

            contacts.append(
                ContactModel(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    description=description,
                )
            )

        return contacts

    @staticmethod
    def _extract_field(fields: dict, field_name: str) -> Optional[str]:
        """
        Helper to safely extract the first value of a field
        """
        values = fields.get(field_name, [])
        if not values:
            return None
        return values[0].get("value")