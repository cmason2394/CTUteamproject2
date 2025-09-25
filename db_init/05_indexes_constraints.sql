-- 05_indexes_constraints.sql
-- Adds audit timestamps, integrity checks, and helpful indexes.
-- Safe to run multiple times.

-- 1) Add audit columns (created_at, updated_at) to domain tables (if missing)
DO $$
DECLARE
  r RECORD;
  tbls TEXT[] := ARRAY[
    'teachers','students','rooms','terms','courses',
    'classes','enrollments','assignments','submissions'
  ];
BEGIN
  FOREACH r IN ARRAY tbls LOOP
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()', r);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()', r);
  END LOOP;
END $$;

-- 2) Generic trigger to keep updated_at current
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$;

-- 3) Attach BEFORE UPDATE triggers to bump updated_at
DO $$
DECLARE
  t TEXT;
  tbls TEXT[] := ARRAY[
    'users','teachers','students','rooms','terms','courses',
    'classes','enrollments','assignments','submissions'
  ];
BEGIN
  FOREACH t IN ARRAY tbls LOOP
    EXECUTE format('
      DO $$
      BEGIN
        IF NOT EXISTS (
          SELECT 1 FROM pg_trigger WHERE tgname = %L
        ) THEN
          EXECUTE %L;
        END IF;
      END $$;
    ', 'trg_'||t||'_updated_at',
       'CREATE TRIGGER '||quote_ident('trg_'||t||'_updated_at')||' BEFORE UPDATE ON '||quote_ident(t)||
       ' FOR EACH ROW EXECUTE FUNCTION set_updated_at()'
    );
  END LOOP;
END $$;

-- 4) Data integrity checks
ALTER TABLE IF EXISTS assignments
  ADD CONSTRAINT IF NOT EXISTS chk_points_positive CHECK (points > 0);

ALTER TABLE IF EXISTS submissions
  ADD CONSTRAINT IF NOT EXISTS chk_score_range CHECK (score IS NULL OR score >= 0);

-- 5) Helpful indexes (foreign keys & common lookups)
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_class   ON enrollments(class_id);
CREATE INDEX IF NOT EXISTS idx_assignments_class   ON assignments(class_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student ON submissions(student_id);
