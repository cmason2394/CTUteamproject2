import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv() # loads .env file

_conn = None

def get_db():
    """
    Get or create a global PostgreSQL connection.
    """
    global _conn
    if _conn is None:
        pg_uri = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/schooldb")
        _conn = psycopg2.connect(pg_uri, cursor_factory=psycopg2.extras.RealDictCursor)

        # Ensure the table exists
        with _conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    id SERIAL PRIMARY KEY,
                    teacher_id INT NOT NULL,
                    class_id INT NOT NULL
                );
            """)
            _conn.commit()

    return _conn


def save_assignment(db_conn, teacher_id, class_id):
    """
    Insert a new assignment row.
    """
    with db_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO assignments (teacher_id, class_id) VALUES (%s, %s)",
            (teacher_id, class_id)
        )
        db_conn.commit()


#def get_assignments_by_teacher(db_
