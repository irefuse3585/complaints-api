# entrypoint.sh

#!/usr/bin/env sh
set -e

# 1) Apply all Alembic migrations before starting the app
alembic upgrade head

# 2) Launch Uvicorn server for FastAPI
exec uvicorn src.main:app --host 0.0.0.0 --port 8000