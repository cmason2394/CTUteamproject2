import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

# Connection factory and context managers
def _pg_dsn() -> str:
    # Expect DATABASE_URL like: postgresql://user:pass@host:5432/schooldb
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not set. Example: postgresql://postgres:pass@localhost:5432/schooldb")
    return dsn + ("?connect_timeout=5" if "connect_timeout" not in dsn else "")

def _connect():
    return psycopg2.connect(_pg_dsn(), cursor_factory=psycopg2.extras.RealDictCursor)

@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@contextmanager
def get_cursor(conn=None):
    owns = False
    if conn is None:
        conn = _connect()
        owns = True
    cur = conn.cursor()
    try:
        yield cur
        if owns:
            conn.commit()
    except Exception:
        if owns:
            conn.rollback()
        raise
    finally:
        cur.close()
        if owns:
            conn.close()

# Business operations aligned to schema
# Assign a teacher to a class (classes.teacher_id is the source of truth)
def assign_teacher_to_class(class_id: int, teacher_id: int) -> None:
    sql = "UPDATE classes SET teacher_id = %s WHERE id = %s"
    with get_conn() as conn, get_cursor(conn) as cur:
        cur.execute(sql, (teacher_id, class_id))

# Fetch all classes for a teacher
def get_classes_by_teacher(teacher_id: int):
    sql = """
        SELECT c.id, c.code, c.title, c.subject, c.term_id, c.room_id
        FROM classes c
        WHERE c.teacher_id = %s
        ORDER BY c.id
    """
    with get_conn() as conn, get_cursor(conn) as cur:
        cur.execute(sql, (teacher_id,))
        return cur.fetchall()

# OPTIONAL: query teacher profile view if present
def get_teacher_profile(teacher_id: int):
    # v_teacher_profile is defined in 01_schema.sql
    sql = "SELECT * FROM v_teacher_profile WHERE teacher_id = %s"
    with get_conn() as conn, get_cursor(conn) as cur:
        cur.execute(sql, (teacher_id,))
        return cur.fetchone()

