from fastapi import APIRouter

from .contacts import router as contacts_router

router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)


router.include_router(contacts_router)

__all__ = ["router"]