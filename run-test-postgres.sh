#!/usr/bin/bash

set -euo pipefail

docker run -d --rm \
  -e POSTGRES_DB=linkding \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres

export PGHOST=localhost
export PGUSER=postgres
export PGPASSWORD=postgres

until psql -qc '\l' >/dev/null; do
  echo >&2 "$(date +%Y%m%dt%H%M%S) Postgres is unavailable - sleeping"
  sleep 1
done
echo >&2 "$(date +%Y%m%dt%H%M%S) Postgres is up - executing command"

python manage.py migrate
