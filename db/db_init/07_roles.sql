-- 07_roles.sql
-- Create least-privilege roles and grants. Adjust passwords as needed.

-- app_user: runtime connection (no DDL)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user LOGIN PASSWORD 'devpassword';
  END IF;
END $$;

GRANT CONNECT ON DATABASE current_database() TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- Grants on existing tables
DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE %I TO app_user', r.tablename);
  END LOOP;
END $$;

-- Ensure future tables get granted automatically (must be run by the owner that creates tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- Optional: db_migrator role for schema changes
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'db_migrator') THEN
    CREATE ROLE db_migrator LOGIN PASSWORD 'migrate_me';
  END IF;
END $$;
GRANT CONNECT ON DATABASE current_database() TO db_migrator;
GRANT USAGE, CREATE ON SCHEMA public TO db_migrator;
