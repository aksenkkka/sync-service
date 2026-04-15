import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_search_contact_endpoint(monkeypatch, client):
    fake_results = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "description": "Test contact",
        }
    ]

    async def fake_search_contacts(query, limit=10, offset=0):
        return fake_results

    monkeypatch.setattr(
        "src.interfaces.contacts.contacts_interface.ContactsInterface.search_contacts",
        fake_search_contacts,
    )

    response = client.get("api/v1/contacts/search?q=john")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["email"] == "john@example.com"