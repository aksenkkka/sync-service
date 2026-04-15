import pytest

from src.interfaces.contacts.contacts_interface import ContactsInterface
from src.models.contacts import ContactModel
from src.repositories.contacts.contacts_repository import ContactsRepository


@pytest.mark.asyncio
async def test_search_contacts(monkeypatch):
    fake_rows = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "description": "Test contact",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "description": "Another contact",
        },
    ]

    async def fake_fetch_all(query, *args):
        return fake_rows

    monkeypatch.setattr(ContactsRepository, "fetch", fake_fetch_all)
    monkeypatch.setattr(ContactsRepository, "_conn", True)
    results = await ContactsInterface.search_contacts("test")
    assert isinstance(results, list)
    assert all(isinstance(r, ContactModel) for r in results)
    assert results[0].email == "john@example.com"