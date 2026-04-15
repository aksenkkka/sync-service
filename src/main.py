from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api import router
from starlette.middleware.cors import CORSMiddleware
from src.config import settings

CSV_PATH = "src/db/populate/Contacts.csv"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.repositories.contacts.contacts_repository import ContactsRepository

    # Startup
    await ContactsRepository.connect(settings.POSTGRESDB_URL)
    await ContactsRepository.ensure_table_and_import(CSV_PATH)
    yield
    # Shutdown
    await ContactsRepository.disconnect()


def create_app() -> FastAPI:
    description = """### Contacts Base"""
    app = FastAPI(
        title="Contacts Base",
        version="1.0.0",
        description=description,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


app = create_app()