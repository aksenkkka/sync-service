# Contacts Search Sync Service

Contacts Search  is a backend service for storing, importing, synchronizing, and searching contact records. The implementation uses **FastAPI**, **PostgreSQL**, **asyncpg**, **Redis**, and **Celery** to provide an asynchronous contact search workflow.

The main API surface is:

```text
GET /api/v1/contacts/search?q=<query>&limit=<limit>&offset=<offset>
```

The endpoint returns contacts matched by name or description using PostgreSQL full-text search.


## What Is Implemented

### Asynchronous API Layer

The application exposes a FastAPI endpoint for contact search:

```text
GET /api/v1/contacts/search
```

The route is implemented as an async handler, so request processing can cooperate with non-blocking database access instead of blocking the server thread while PostgreSQL responds.

This is useful for a contact search service because multiple users can search at the same time while the application waits for database I/O.

### PostgreSQL Full-Text Search

Search is implemented with PostgreSQL `to_tsvector`, `plainto_tsquery`, and `ts_rank_cd`.

The query searches across:

- first name;
- last name;
- description.

Results are ordered by relevance, not just by insertion order. This makes the search endpoint more useful than a basic `LIKE '%query%'` filter, because PostgreSQL can tokenize text, match natural words, and rank stronger matches higher.


### Upsert-Based Contact Sync

Contacts are synchronized by email, which is treated as a unique identifier.

The repository uses PostgreSQL `ON CONFLICT (email) DO UPDATE`, so repeated syncs do not create duplicate contacts. Existing contacts are updated with the newest name and description values.

This makes the sync process idempotent: the same contact can be imported or fetched multiple times without corrupting the dataset.

### External Contacts Provider Integration

The interface layer includes an async HTTP client built with `httpx`.

It fetches contacts from an external contacts API, extracts useful fields from the provider response, skips invalid records without email, and converts valid records into `ContactModel` objects.

The result is a small integration layer that separates third-party API parsing from database persistence.

### Scheduled Background Sync

The project includes Celery and Celery Beat.

Celery Beat schedules the contact synchronization task every 30 seconds, and the Celery worker runs the task in the background. Redis is used as the broker.

This keeps the API responsive: contact synchronization does not have to run inside a user request, and the search endpoint can stay focused on reading already prepared data.

### Dockerized Local Environment

The project includes Docker Compose services for:

- backend API;
- PostgreSQL;
- Redis;
- Celery worker;
- Celery Beat scheduler.


## Tech Stack

| Area | Technology |
| --- | --- |
| API | FastAPI, Uvicorn |
| Database | PostgreSQL, asyncpg |
| Background jobs | Celery, Celery Beat |
| Message broker | Redis |
| HTTP client | httpx |
| Data validation | Pydantic |
| Configuration | pydantic-settings, python-dotenv |
| Testing | pytest, pytest-asyncio, FastAPI TestClient |
| Package manager | uv |
| Runtime | Python 3.12 |

## Project Structure

```text
src/
|-- api/
|   `-- contacts/
|       `-- api.py                 # HTTP endpoint for contact search
|-- db/
|   `-- populate/
|       `-- Contacts.csv           # initial contacts dataset
|-- interfaces/
|   `-- contacts/
|       `-- contacts_interface.py  # search and external API sync logic
|-- models/
|   `-- contacts.py                # Pydantic contact model
|-- repositories/
|   `-- contacts/
|       |-- base.py                # asyncpg connection helpers
|       `-- contacts_repository.py # table creation, CSV import, upsert
|-- tasks/
|   `-- cron_tasks.py              # Celery task for contact sync
|-- config.py                      # environment-based settings
|-- main.py                        # FastAPI app factory and lifespan
`-- worker.py                      # Celery app and Beat schedule
```

## API Reference

### Search Contacts

```http
GET /api/v1/contacts/search?q=john&limit=10&offset=0
```

Query parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `q` | string | yes | Search phrase used by PostgreSQL full-text search |
| `limit` | integer | no | Maximum number of contacts to return. Default: `10` |
| `offset` | integer | no | Number of matched contacts to skip. Default: `0` |





## Running Locally

Install dependencies:

```bash
uv sync
```

Run the API:

```bash
uv run uvicorn src.main:app --reload --port 8080
```

Open the API docs:

```text
http://127.0.0.1:8080/docs
```

## Running With Docker Compose

Start the full environment:

```bash
docker compose up --build
```

The backend will be available at:

```text
http://127.0.0.1:8080
```


## How the Search Flow Works

1. The application starts and opens an async PostgreSQL connection.
2. The contacts table is created if it does not exist.
3. Initial contacts are imported from `Contacts.csv` when the table is empty.
4. A client requests `/api/v1/contacts/search`.
5. The interface layer builds a PostgreSQL full-text search query.
6. PostgreSQL ranks matching contacts by relevance.
7. Rows are converted into `ContactModel` responses.
8. The API returns a clean JSON list to the client.

## How the Sync Flow Works

1. Celery Beat schedules `sync_contacts` every 30 seconds.
2. The worker opens a PostgreSQL connection.
3. The interface fetches contacts from the external provider with `httpx`.
4. Provider-specific fields are normalized into the internal `ContactModel`.
5. Contacts without email are skipped because email is required for uniqueness.
6. Valid contacts are upserted into PostgreSQL by email.

## Tests

Run tests with:

```bash
uv run pytest
```

The test suite covers:

- the `/api/v1/contacts/search` endpoint;
- conversion of repository rows into `ContactModel` objects;
- async contact search behavior with mocked repository access.

