# School Management System — SQL Pack (PostgreSQL)

This pack mirrors the MongoDB design in relational form for teams/supervisors who want to review a SQL model. It includes DDL, dev seed data, reference queries for your user stories, and an `assign_room` function with a conflict check. It uses PostgreSQL features (indexes, constraints, and an optional exclusion constraint approach).

# School DB: Setup & Integration

This folder contains SQL and helper files so every teammate can spin up and use the database consistently.

## Files
- 01_schema.sql — Tables: `users`, `roles`, `user_roles`, `teachers`, `students`, `rooms`, `terms`, `courses`, `classes`, `enrollments`, `assignments`, `submissions`. Includes constraints + indexes.
- 02_seed.sql — Optional developer seed data.
- 03_queries.sql — Reference queries for:
  - View class information (teacher, students, room, schedule)
  - Teacher dashboards: my profile, my classes, my students’ performance
- 04_functions.sql — `assign_room(class_id, room_id)` with a schedule conflict check (simple) and notes on a robust exclusion-constraint alternative.
- `05_indexes_constraints.sql` — audit timestamps, integrity checks, useful indexes
- `06_functions_wrapped.sql` — JSON-returning helper functions
- `07_roles.sql` — least-privilege roles and grants
- `docker-compose.yml` — local Postgres with auto-init support
- `scripts/migrate.sh` — applies schema + migrations
- `scripts/seed.sh` — re-applies seeds

> You can place the SQL files inside `db_init/` and bring up Docker. On first start, Postgres will run them in lexical order.

## Quick Start (Docker)

```bash
# In this directory
mkdir -p db_init
cp 01_schema.sql 02_seed.sql 05_indexes_constraints.sql 06_functions_wrapped.sql 07_roles.sql db_init/

docker compose up -d
# Wait for container to become healthy

# Optionally run scripts from host if you prefer
./scripts/migrate.sh
```

Postgres will start with:
- user: `postgres`
- password: `postgres`
- database: `school_app`
- port: `5432`

## Quick Start (Local Postgres)

```bash
export PGPASSWORD=postgres
psql -h localhost -U postgres -d school_app -f 01_schema.sql
psql -h localhost -U postgres -d school_app -f 02_seed.sql
psql -h localhost -U postgres -d school_app -f 05_indexes_constraints.sql
psql -h localhost -U postgres -d school_app -f 06_functions_wrapped.sql
psql -h localhost -U postgres -d school_app -f 07_roles.sql
```

## App Integration

Use environment variables (example `.env`):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=school_app
DB_USER=app_user
DB_PASSWORD=devpassword
```

### Node.js (pg)

```js
const { Pool } = require('pg');
require('dotenv').config();
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD
});

async function classInfo(id) {
  const { rows } = await pool.query('SELECT get_class_info($1) AS data', [id]);
  return rows[0].data;
}
```

### Python (SQLAlchemy Core)

```python
from sqlalchemy import create_engine, text
import os

db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"          f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(db_url)

with engine.connect() as conn:
    data = conn.execute(text('SELECT get_class_info(:cid) AS data'), {'cid': 1}).scalar()
    print(data)
```

## Notes

- Emails use `CITEXT`, so uniqueness is case-insensitive.
- Runtime role is `app_user` (no DDL); keep schema changes under a separate owner or `db_migrator`.
- The `set_updated_at` trigger keeps `updated_at` fresh.
- Helper functions return JSONB so your API team can `SELECT get_*()` and return it directly.
