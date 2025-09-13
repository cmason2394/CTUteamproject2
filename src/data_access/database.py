def save_assignment(db_conn, teacher_id, class_id):
  cursor = db_conn.cursor()
  cursor.execute(
    "INSERT INTO assignments ( teacher_id, class_id) VALUES (?, ?)",
    (teacher_id, class_id)
  )
  db_conn.commit()
def get_assignments_by_teacher(db_conn, teracher_id):
  cursor = db_conn.cursor()
  cursor.execute(
    "SELECT class_id FROM assignment WHERE teacher_id = ?",
    (teacher_id,)
  )
  return cursor.fetchall()   # SQLite code, will have to adapt if we use MongoDB or other database.
