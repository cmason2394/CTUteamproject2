import psycopg2
import psycopg2.extras
import json

class GradeManager:
    def __init__(self, uri="postgresql://postgres:password@localhost:5432/schooldb"):
        self.conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)

        # Ensure table exists
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    student_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    grades JSONB DEFAULT '{}'::jsonb
                );
            """)
            self.conn.commit()

    def add_student(self, student_id, name):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            if cur.fetchone():
                print("Student already exists.")
                return

            cur.execute(
                "INSERT INTO students (student_id, name, grades) VALUES (%s, %s, %s)",
                (student_id, name, json.dumps({}))
            )
            self.conn.commit()
        print(f"Student {name} added successfully.")

    def record_grade(self, student_id, assignment, grade):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE students
                SET grades = jsonb_set(
                    COALESCE(grades, '{}'::jsonb),
                    %s,
                    %s,
                    true
                )
                WHERE student_id = %s
                RETURNING *;
                """,
                ([assignment], json.dumps(grade), student_id)
            )
            result = cur.fetchone()
            self.conn.commit()

        if result:
            print(f"Grade recorded: {student_id} - {assignment}: {grade}")
        else:
            print("Student not found.")

    def view_grades(self, student_id=None):
        with self.conn.cursor() as cur:
            if student_id:
                cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
                student = cur.fetchone()
                if student:
                    print(f"Grades for {student['name']}:")
                    for assignment, grade in (student["grades"] or {}).items():
                        print(f"  {assignment}: {grade}")
                else:
                    print("Student not found.")
            else:
                cur.execute("SELECT * FROM students")
                for student in cur.fetchall():
                    print(f"\nGrades for {student['name']}:")
                    for assignment, grade in (student["grades"] or {}).items():
                        print(f"  {assignment}: {grade}")
