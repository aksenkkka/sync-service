FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml uv.lock* ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN echo "${DEBUG}"

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    lsb-release wget  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN uv venv --python 3.12 ./.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN uv sync

RUN chmod 777 "$VIRTUAL_ENV/bin/celery"

COPY . /app/

COPY scripts/ /app/scripts/
RUN chmod -R 777 /app/scripts/