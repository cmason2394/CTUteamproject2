-- db_sql/02_seed.sql
-- Developer seed data

INSERT INTO roles (name, description) VALUES
  ('admin','Administrator'),
  ('teacher','Teacher'),
  ('student','Student')
ON CONFLICT (name) DO NOTHING;

-- Users
INSERT INTO users (email, password_hash, first_name, last_name)
VALUES
  ('admin@example.com','<bcrypt>','Admin','User'),
  ('teacher@example.com','<bcrypt>','Ada','Lovelace'),
  ('student@example.com','<bcrypt>','Grace','Hopper')
ON CONFLICT (email) DO NOTHING;

-- Role links
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u CROSS JOIN roles r
WHERE (u.email='admin@example.com' AND r.name='admin')
ON CONFLICT DO NOTHING;
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u CROSS JOIN roles r
WHERE (u.email='teacher@example.com' AND r.name='teacher')
ON CONFLICT DO NOTHING;
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u CROSS JOIN roles r
WHERE (u.email='student@example.com' AND r.name='student')
ON CONFLICT DO NOTHING;

-- Profiles
INSERT INTO teachers (user_id, employee_no, department_code)
SELECT id, 'EMP-1001', 'CS' FROM users WHERE email='teacher@example.com'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO students (user_id, student_no, grade_level)
SELECT id, 'S-0001', 12 FROM users WHERE email='student@example.com'
ON CONFLICT (user_id) DO NOTHING;

-- Terms, Rooms, Courses
INSERT INTO terms (code, name, start_date, end_date)
VALUES ('2025-FALL','Fall 2025','2025-08-25','2025-12-15')
ON CONFLICT (code) DO NOTHING;

INSERT INTO rooms (code, capacity) VALUES ('B-204',40)
ON CONFLICT (code) DO NOTHING;

INSERT INTO courses (code, title, subject, credits)
VALUES ('CS-101','Intro to CS','Computer Science',3.0)
ON CONFLICT (code) DO NOTHING;

-- Class
INSERT INTO classes (course_id, code, title, subject, teacher_id, term_id, room_id, days_int, start_min, end_min)
SELECT c.id, 'CS-101-01', 'Intro to CS', 'Computer Science', t.id, tm.id, r.id, ARRAY[1,3,5], 600, 650
FROM courses c, teachers t, terms tm, rooms r
WHERE c.code='CS-101' AND t.employee_no='EMP-1001' AND tm.code='2025-FALL' AND r.code='B-204'
ON CONFLICT (code, term_id) DO NOTHING;

-- Enrollment
INSERT INTO enrollments (student_id, class_id)
SELECT s.id, cl.id
FROM students s, classes cl
WHERE s.student_no='S-0001' AND cl.code='CS-101-01'
ON CONFLICT (student_id, class_id) DO NOTHING;

-- Assignment & submission
INSERT INTO assignments (class_id, title, points)
SELECT id, 'HW1', 100.0 FROM classes WHERE code='CS-101-01'
ON CONFLICT DO NOTHING;

INSERT INTO submissions (assignment_id, student_id, score)
SELECT a.id, s.id, 95.0
FROM assignments a, students s
WHERE a.title='HW1' AND s.student_no='S-0001'
ON CONFLICT (assignment_id, student_id) DO NOTHING;
