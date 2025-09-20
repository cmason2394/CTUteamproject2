from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.onjectid import ObjectId
import os, secrets
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.get_database("placeholder") # Change to db name
users = db.users

parent_bp = Blueprint("parent", __name__)

def user_by_id(uid):
    try:
        return users.find_one({"_id": ObjectId(uid)})
    except:
        return None

def user_by_email(email):
    return users.find_one({"email": email.lower()})

# Auth: register (student or parent)
@parent_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = (data.get("email") or "").lower()
    password = data.get("password")
    role = data.get("role", "parent") # Default parent
    if not (name and email and password):
        return jsonify({"msg":"name, email, password required"}), 400
    if user_by_email(email):
        return jsonify({"msg":"email already registered"}), 400
    
    pwd_hash = generate_password_hash(password)
    doc = {
        "name": name,
        "email": email,
        "password_hash": pwd_hash,
        "role": role,
    }
    if role == "parent":
        doc["children"] = []       # list of student ObjectId strings
    if role == "student":
        # Student: classes and grades arrays + share_code for parent linking
        doc["classes"] = []
        doc["grades"] = []
        doc["share_code"] = secrets.token_urlsafe(6)           # short code safe to share
    res = users.insert_one(doc)
    doc_id = str(res.inserted_id)
    return jsonify({"id": doc_id, "share_code": doc.get("share_code")}), 201

# Auth Login
@parent_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or ""()).lower()
    password = data.get("password")
    user = user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg":"Bad email/password"}), 401
    access_token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": access_token, "role": user["role"]})
    
# Parent: associate to a child using student id + share_code
@parent_bp.route("/parents/associate", methods=["POST"])
@jwt_required()
def associate_child():
    parent_id = get_jwt_identity()
    parent = user_by_id(parent_id)
    if not parent or parent.get("role") != "parent":
        return jsonify({"msg":"only parents can perform this"}), 403
    
    data = request.get_json() or {}
    student_id = data.get("student_id")
    share_code = data.get("share_code")
    if not student_id or not share_code:
        return jsonify({"msg":"student_id and share_code rquired"}), 400
    student = user_by_id(student_id)
    if not student or student.get("role") != "student":
        return jsonify({"msg":"Student not found"}), 404
    if student.get("share_code") != share_code:
        return jsonify({"msg":"Invalid share_code"}), 403
    
    # Add student to parent's childern if not present
    if ObjectId(student_id) not in parent.get("children", []):
        users.update_one({"_id": ObjectId(parent_id)}, {"$addToSet":{"children": ObjectId(student_id)}})
        
    return jsonify({"msg":"Child associated"}), 200
# Parent: list children with summary (info + grades)
@parent_bp.route("/parents/children", methods=["GET"])
@jwt_required()
def list_children():
    parent_id = get_jwt_identity()
    parent = user_by_id(parent_id)
    if not parent or parent.get("role") != "parent":
        return jsonify({"msg":"Only parents can perform this"}), 403
    
    children_ids = parent.get("children", [])
    # convert ObjectIds -> query
    child_docs = []
    for c in children_ids:
        child = users.find_one({"_id": c, "role":"student"}, {"password+hash":0})
        if child:
            # Simple summary: name + latest grades
            summary = {
                "id": str(child["_id"]),
                "name": child.get("name"),
                "classes": child.get("classes", []),
                "grades": child.get("grades", []),
            }
            child_docs.append(summary)
        return jsonify({"children": child_docs})

# Parent: get detailed child view (guarded)
@parent_bp.route("/parents/children/<student_id>", methods=["GET"])
@jwt_required()
def child_detail(student_id):
    parent_id = get_jwt_identity()
    parent = user_by_id(parent_id)
    if not parent or parent.get("role") != "parent":
        return jsonify({"msg":"Only parents can perform this"}), 403
    
    # Ensure the student is in parent's children
    if ObjectId(student_id) not in parent.get("children", []):
        return jsonify({"msg":"Forbidden: not associated with this child"}), 403
    
    child = user_by_id(student_id)
    if not child or child.get("role") != "student":
        return jsonify({"msg":"Student not found"}), 404
    
    # Hide sensitive fields:
        child.pop("password_hash", None)
        child.pop("share_code", None)
        child["_id"] = str(child["_id"])
        # Return whatever you store for academics
        return jsonify(child)
