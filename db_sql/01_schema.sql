-- db_sql/01_schema.sql
-- PostgreSQL schema for School Management System

CREATE EXTENSION IF NOT EXISTS citext;

-- RBAC
CREATE TABLE roles (
  id BIGSERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT
);

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email CITEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

-- Organization
CREATE TABLE teachers (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  employee_no TEXT UNIQUE NOT NULL,
  department_code TEXT
);

CREATE TABLE students (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  student_no TEXT UNIQUE NOT NULL,
  grade_level SMALLINT
);

CREATE TABLE rooms (
  id BIGSERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  capacity INT NOT NULL CHECK (capacity > 0)
);

CREATE TABLE terms (
  id BIGSERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL, -- e.g., 2025-FALL
  name TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  CHECK (start_date < end_date)
);

CREATE TABLE courses (
  id BIGSERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  subject TEXT,
  credits NUMERIC(3,1) DEFAULT 3.0
);

-- CLASSES (sections)
CREATE TABLE classes (
  id BIGSERIAL PRIMARY KEY,
  course_id BIGINT REFERENCES courses(id) ON DELETE SET NULL,
  code TEXT NOT NULL,          -- section code e.g., CS-101-01
  title TEXT NOT NULL,
  subject TEXT,
  teacher_id BIGINT NOT NULL REFERENCES teachers(id) ON DELETE RESTRICT,
  term_id BIGINT NOT NULL REFERENCES terms(id) ON DELETE RESTRICT,
  room_id BIGINT REFERENCES rooms(id) ON DELETE SET NULL,

  -- simple schedule
  days TEXT[],
  start_time TIME,
  end_time TIME,

  -- numeric schedule (recommended)
  days_int SMALLINT[],         -- e.g., {1,3,5}
  start_min INT,               -- 600 for 10:00
  end_min INT,                 -- 650 for 10:50

  CONSTRAINT uq_class_code_term UNIQUE (code, term_id),
  CONSTRAINT chk_time_order CHECK (
    (start_time IS NULL OR end_time IS NULL OR start_time < end_time)
    AND (start_min IS NULL OR end_min IS NULL OR start_min < end_min)
  )
);

CREATE INDEX idx_classes_teacher ON classes(teacher_id);
CREATE INDEX idx_classes_room ON classes(room_id);
CREATE INDEX idx_classes_term ON classes(term_id);

-- Enrollments
CREATE TABLE enrollments (
  id BIGSERIAL PRIMARY KEY,
  student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  class_id BIGINT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
  UNIQUE (student_id, class_id)
);

-- Assignments / Submissions
CREATE TABLE assignments (
  id BIGSERIAL PRIMARY KEY,
  class_id BIGINT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  points NUMERIC(6,2) NOT NULL DEFAULT 100.0
);

CREATE TABLE submissions (
  id BIGSERIAL PRIMARY KEY,
  assignment_id BIGINT NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
  student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  score NUMERIC(6,2),
  UNIQUE (assignment_id, student_id)
);

CREATE VIEW v_teacher_profile AS
SELECT t.id AS teacher_id, u.id AS user_id, u.email, u.first_name, u.last_name, t.employee_no, t.department_code
FROM teachers t JOIN users u ON u.id = t.user_id;

-- See 04_functions.sql for assign_room() and notes on exclusion constraints.
