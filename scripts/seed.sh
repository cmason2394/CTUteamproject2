#!/usr/bin/env bash
set -euo pipefail
: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=school_app}"
: "${DB_USER:=postgres}"
: "${DB_PASSWORD:=postgres}"

export PGPASSWORD="$DB_PASSWORD"

if [[ -f "02_seed.sql" ]]; then
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "02_seed.sql"
else
  echo "02_seed.sql not found"
fi
