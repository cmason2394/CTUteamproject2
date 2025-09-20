# Seed sample to generate sample student + parent
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os, secrets
MONGO_URI = os.getenv ("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.get_database("database") # Change to actual database
users = db.users
users.delete_many({}) # careful in real Database

# Sample Student
student = {
  "name": "Jane Doe",
  "email": "alice@student.edu",
  "password_hash": generate_password_hash("studentpass"),
  "role": "student",
  "classes": [{"class_id":"MATH101","name":"Algebra I"}],
  "grades": {["class_id":"MATH101","grade":"A-"}],
  "share_code": secrets.token_urlsafe(6)
}
sid = user.insert_one(student).inserted_id
print("Student id:", sid, "share_code:", student["share_code"])

# Sample Parent
parent = {
  "name": "Parent One",
  "email": "parent@example.com",
  "password_hash": generate_password_hash("parentpass"),
  "role":"parent",
  "children": []
}
pid = users.insert_one(parent).inserted_id
print("Parent id:", pid)
