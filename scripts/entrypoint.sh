#!/bin/bash
set -euo pipefail
ENVIRONMENT="${ENVIRONMENT:-}"
DEBUG="${DEBUG:-}"
WORKERS="${WORKERS:-}"


if [[ ! "$ENVIRONMENT" =~ ^(LOCAL|DEV|STAGE|PRODUCTION)$ ]]; then
  echo "ENVIRONMENT must be one of: LOCAL, DEV, STAGE, PRODUCTION, got $ENVIRONMENT"
  exit 1
fi


case "$ENVIRONMENT" in
  LOCAL|DEV)
    DEBUG=True
    echo "Local/Dev development"
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
    ;;

  STAGE)
    if [[ "$DEBUG" == "True" ]]; then
      echo "STAGE with DEBUG=true: running single worker"
      uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
    else
      if ! [[ "$WORKERS" =~ ^[1-9][0-9]*$ ]]; then
        echo "WORKERS must be a positive integer in STAGE when DEBUG=false"
        exit 1
      fi
      echo "STAGE: Running with $WORKERS workers"
      uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --workers "$WORKERS"
    fi
    ;;

  PRODUCTION)
    DEBUG=False
    if ! [[ "$WORKERS" =~ ^[1-9][0-9]*$ ]]; then
      echo "WORKERS must be a positive integer in PRODUCTION"
      exit 1
    fi
    echo "PRODUCTION: Running with $WORKERS workers, DEBUG=false"
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --workers "$WORKERS"
    ;;
esac