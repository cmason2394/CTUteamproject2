# School Management System — SQL Pack (PostgreSQL)

This pack mirrors the MongoDB design in relational form for teams/supervisors who want to review a SQL model. It includes DDL, dev seed data, reference queries for your user stories, and an `assign_room` function with a conflict check. It uses PostgreSQL features (indexes, constraints, and an optional exclusion constraint approach).

## Files
- **01_schema.sql** — Tables: `users`, `roles`, `user_roles`, `teachers`, `students`, `rooms`, `terms`, `courses`, `classes`, `enrollments`, `assignments`, `submissions`. Includes constraints + indexes.
- **02_seed.sql** — Optional developer seed data.
- **03_queries.sql** — Reference queries for:
  - View class information (teacher, students, room, schedule)
  - Teacher dashboards: my profile, my classes, my students’ performance
- **04_functions.sql** — `assign_room(class_id, room_id)` with a schedule conflict check (simple) and notes on a robust exclusion-constraint alternative.

## Quick start
```bash
createdb school_ms
psql -d school_ms -f db_sql/01_schema.sql
psql -d school_ms -f db_sql/02_seed.sql   # optional
psql -d school_ms -f db_sql/03_queries.sql
psql -d school_ms -f db_sql/04_functions.sql
```

> NOTE: The app you’re building is MongoDB-first. This SQL pack is for parity / comparison / future migrations or professors who want to see a relational equivalent.
