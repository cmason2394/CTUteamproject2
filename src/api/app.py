import os
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from src.data_access.database import get_db
from .parent_access import parent_bp

app = Flask(__name__)

# PostgreSQL connection
conn = get_db()

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me-in-prod')
jwt = JWTManager(app)

# Register blueprint
app.register_blueprint(parent_bp, url_prefix="/api")

# Partial update endpoint for admin
@app.route("/api/classAssignments/<int:id>", methods=["PUT"])
def update_class_assignment(id):
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    # Allowed updatable fields
    allowed_fields = ["subject", "teacherId", "studentIds", "classroom", "classTime"]
    update_fields = {k: data[k] for k in allowed_fields if k in data}

    if not update_fields:
        return jsonify({"error": "No valid updatable fields provided"}), 400

    set_clauses = []
    values = []
    i = 1
    for key, val in update_fields.items():
        set_clauses.append(f"{key} = %s")
        values.append(val)
        i += 1
    values.append(id)

    sql = f"UPDATE class_assignments SET {', '.join(set_clauses)} WHERE id = %s RETURNING *;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, values)
            updated = cur.fetchone()
            conn.commit()

            if not updated:
                return jsonify({"error": "Class not found"}), 404

            return jsonify(updated), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # run with: python app.py
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
