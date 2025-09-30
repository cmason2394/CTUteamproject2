from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
import os, secrets
from src.data_access.database import get_conn
from dotenv import load_dotenv

load_dotenv()

# Connect to PostgreSQL
conn = get_conn()

parent_bp = Blueprint("parent", __name__)

# --- Helper queries ---
def user_by_id(uid):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (uid,))
            return cur.fetchone()
    except Exception:
        return None

def user_by_email(email):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email.lower(),))
        return cur.fetchone()


# --- Auth: register (student or parent) ---
@parent_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = (data.get("email") or "").lower()
    password = data.get("password")
    role = data.get("role", "parent")  # Default parent

    if not (name and email and password):
        return jsonify({"msg": "name, email, password required"}), 400

    if user_by_email(email):
        return jsonify({"msg": "email already registered"}), 400

    pwd_hash = generate_password_hash(password)
    share_code = None
    children = None
    classes, grades = None, None

    if role == "parent":
        children = []  # store as int[] in Postgres
    if role == "student":
        classes, grades = [], []
        share_code = secrets.token_urlsafe(6)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (name, email, password_hash, role, children, classes, grades, share_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, share_code;
                """,
                (name, email, pwd_hash, role, children, classes, grades, share_code),
            )
            new_user = cur.fetchone()
            conn.commit()
        return jsonify({"id": new_user["id"], "share_code": new_user.get("share_code")}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 500


# --- Auth Login ---
@parent_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").lower()
    password = data.get("password")

    user = user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg": "Bad email/password"}), 401

    access_token = create_access_token(identity=user["id"])
    return jsonify({"access_token": access_token, "role": user["role"]})


# --- Parent: associate to a child using student id + share_code ---
@parent_bp.route("/parents/associate", methods=["POST"])
@jwt_required()
def associate_child():
    parent_id = get_jwt_identity()
    parent = user_by_id(parent_id)

    if not parent or parent.get("role") != "parent":
        return jsonify({"msg": "only parents can perform this"}), 403

    data = request.get_json() or {}
    student_id = data.get("student_id")
    share_code = data.get("share_code")

    if not student_id or not share_code:
        return jsonify({"msg": "student_id and share_code required"}), 400

    student = user_by_id(student_id)
    if not student or student.get("role") != "student":
        return jsonify({"msg": "Student not found"}), 404
    if student.get("share_code") != share_code:
        return jsonify({""})
