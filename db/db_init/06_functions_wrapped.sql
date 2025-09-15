-- 06_functions_wrapped.sql
-- Wrap JSON reference queries as functions for easy reuse.

-- get_class_info: returns a single class with roster, teacher, room, and schedule
CREATE OR REPLACE FUNCTION get_class_info(p_class_id BIGINT)
RETURNS JSONB
LANGUAGE sql
AS $$
WITH base AS (
  SELECT cl.id AS class_id, cl.code, cl.title, cl.subject, cl.term_id, cl.days_int, cl.start_min, cl.end_min,
         r.id AS room_id, r.code AS room_code, r.capacity AS room_capacity,
         t.id AS teacher_id, t.employee_no, u.email AS teacher_email, u.first_name||' '||u.last_name AS teacher_name
  FROM classes cl
  LEFT JOIN rooms r       ON r.id = cl.room_id
  JOIN teachers t         ON t.id = cl.teacher_id
  JOIN users u            ON u.id = t.user_id
  WHERE cl.id = p_class_id
),
roster AS (
  SELECT e.class_id, s.id AS student_id, s.student_no,
         su.email AS student_email, su.first_name||' '||su.last_name AS student_name, s.grade_level
  FROM enrollments e JOIN students s ON s.id = e.student_id
  JOIN users su ON su.id = s.user_id
  WHERE e.class_id = p_class_id
)
SELECT jsonb_build_object(
  'id', b.class_id,
  'code', b.code,
  'title', b.title,
  'subject', b.subject,
  'term_id', b.term_id,
  'schedule', jsonb_build_object('daysInt', b.days_int, 'startMin', b.start_min, 'endMin', b.end_min),
  'room', CASE WHEN b.room_id IS NULL THEN NULL ELSE jsonb_build_object('id', b.room_id, 'code', b.room_code, 'capacity', b.room_capacity) END,
  'teacher', jsonb_build_object('id', b.teacher_id, 'employee_no', b.employee_no, 'name', b.teacher_name, 'email', b.teacher_email),
  'students', COALESCE(jsonb_agg(jsonb_build_object(
      'id', r.student_id, 'student_no', r.student_no, 'name', r.student_name, 'email', r.student_email, 'grade_level', r.grade_level
    ) ORDER BY r.student_no) FILTER (WHERE r.student_id IS NOT NULL), '[]'::jsonb)
)
FROM base b LEFT JOIN roster r ON r.class_id = b.class_id
GROUP BY b.class_id, b.code, b.title, b.subject, b.term_id, b.days_int, b.start_min, b.end_min, b.room_id, b.room_code, b.room_capacity, b.teacher_id, b.employee_no, b.teacher_name, b.teacher_email;
$$;

-- get_teacher_me: returns the teacher user profile
CREATE OR REPLACE FUNCTION get_teacher_me(p_teacher_user_id BIGINT)
RETURNS JSONB
LANGUAGE sql
AS $$
SELECT jsonb_build_object(
  'id', u.id, 'email', u.email, 'first_name', u.first_name, 'last_name', u.last_name,
  'employee_no', t.employee_no, 'department_code', t.department_code
)
FROM teachers t JOIN users u ON u.id = t.user_id
WHERE u.id = p_teacher_user_id;
$$;

-- get_teacher_classes: returns array of classes the teacher is teaching
CREATE OR REPLACE FUNCTION get_teacher_classes(p_teacher_user_id BIGINT)
RETURNS JSONB
LANGUAGE sql
AS $$
SELECT COALESCE(jsonb_agg(jsonb_build_object(
  'id', cl.id, 'code', cl.code, 'title', cl.title, 'subject', cl.subject, 'term_id', cl.term_id,
  'room_code', r.code, 'schedule', jsonb_build_object('daysInt', cl.days_int, 'startMin', cl.start_min, 'endMin', cl.end_min)
) ORDER BY cl.term_id, cl.code), '[]'::jsonb)
FROM classes cl
LEFT JOIN rooms r ON r.id = cl.room_id
JOIN teachers t ON t.id = cl.teacher_id
WHERE t.user_id = p_teacher_user_id;
$$;

-- get_teacher_performance: list of students with average score and submissions
CREATE OR REPLACE FUNCTION get_teacher_performance(
  p_teacher_user_id BIGINT,
  p_term_id BIGINT DEFAULT NULL,
  p_class_code TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE sql
AS $$
WITH t_classes AS (
  SELECT cl.id FROM classes cl JOIN teachers t ON t.id = cl.teacher_id
  WHERE t.user_id = p_teacher_user_id
  AND (p_term_id IS NULL OR cl.term_id = p_term_id)
  AND (p_class_code IS NULL OR cl.code = p_class_code)
),
s_rows AS (
  SELECT s.id AS student_id, s.student_no
  FROM enrollments e JOIN students s ON s.id = e.student_id
  WHERE e.class_id IN (SELECT id FROM t_classes)
),
scores AS (
  SELECT sub.student_id, AVG(sub.score) AS avg_score, COUNT(*) AS submissions
  FROM submissions sub
  JOIN assignments a ON a.id = sub.assignment_id
  WHERE a.class_id IN (SELECT id FROM t_classes)
  GROUP BY sub.student_id
)
SELECT COALESCE(jsonb_agg(jsonb_build_object(
  'student_id', s.student_id, 'student_no', s.student_no,
  'avg_score', sc.avg_score, 'submissions', COALESCE(sc.submissions,0)
) ORDER BY s.student_no), '[]'::jsonb)
FROM s_rows s
LEFT JOIN scores sc ON sc.student_id = s.student_id;
$$;
