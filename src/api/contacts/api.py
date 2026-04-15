from __future__ import annotations

from typing import List

from fastapi import APIRouter, Query

from src.interfaces.contacts.contacts_interface import ContactsInterface
from src.models.contacts import ContactModel

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("/search", response_model=List[ContactModel])
async def search_contact(
    q: str = Query(..., description="Search query"),
    limit: int | None = 10,
    offset: int = 0):
    """
    Full-text search for contacts by name, email, or description.
    """
    results = await ContactsInterface.search_contacts(q, limit, offset)
    return results