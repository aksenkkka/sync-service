from pydantic import BaseModel
from typing import Optional

class ContactModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    description: Optional[str] = None

