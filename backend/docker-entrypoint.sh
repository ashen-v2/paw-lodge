#!/bin/sh
set -eu

python - <<'PY'
import sys
import time

from sqlalchemy import create_engine, text

from app.core.config import settings

engine = create_engine(settings.database_url)
last_error = None
for _ in range(30):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        sys.exit(0)
    except Exception as exc:  # database may still be starting
        last_error = exc
        time.sleep(1)

print(f"Database not ready: {last_error}", file=sys.stderr)
sys.exit(1)
PY

alembic upgrade head
exec "$@"
