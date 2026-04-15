import csv
from pathlib import Path
from typing import Optional

from .base import BaseRepository


class ContactsRepository(BaseRepository):
    TABLE_NAME = "contacts"

    @classmethod
    async def upsert_contact(
        cls,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Adding new contacts by unique email. Overwriting existing
        contacts with the fetched ones
        """
        query = """
        INSERT INTO contacts (email, first_name, last_name, description)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (email) DO UPDATE
        SET first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            description = EXCLUDED.description
        """
        await cls.execute(query, email, first_name, last_name, description)

    @classmethod
    async def ensure_table_and_import(cls, csv_path: str):
        """
        Check if the table exists. Fallback to creating one.
        Performs initial contacts import either way
        """
        exists_query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{cls.TABLE_NAME}'
        );
        """
        exists = await cls.fetch_one(exists_query)

        if exists and exists["exists"]:
            await cls.import_from_csv(csv_path)
            return

        await cls.execute(f"""
            CREATE TABLE {cls.TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE NOT NULL,
                description TEXT
            );
        """)

        await cls.import_from_csv(csv_path)

    @classmethod
    async def import_from_csv(cls, csv_path: str):
        """
        Inserts contacts to DB from csv file
        """
        exists_query = f"""
            SELECT * FROM {cls.TABLE_NAME};
        """

        data = await cls.fetch_one(exists_query)
        print(data)
        if not data:
            path = Path(csv_path)
            if not path.exists():
                return

            with path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=",")
                for row in reader:
                    await cls.execute(
                        f"""
                        INSERT INTO {cls.TABLE_NAME} (first_name, last_name, email, description)
                        VALUES ($1, $2, $3, $4);
                        """,
                        row.get("first name"),
                        row.get("last name"),
                        row.get("email"),
                        row.get("description"),
                    )