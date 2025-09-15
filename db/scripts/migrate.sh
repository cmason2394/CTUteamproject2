#!/usr/bin/env bash
set -euo pipefail
: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=school_app}"
: "${DB_USER:=postgres}"
: "${DB_PASSWORD:=postgres}"

export PGPASSWORD="$DB_PASSWORD"

# Apply base schema and subsequent migration files in lexical order
for f in 01_schema.sql 02_seed.sql 05_indexes_constraints.sql 06_functions_wrapped.sql 07_roles.sql; do
  if [[ -f "$f" ]]; then
    echo "Applying $f"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$f"
  fi
done

echo "Done."
