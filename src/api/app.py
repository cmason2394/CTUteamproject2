import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/schooldb")
mongo = PyMongo(app)
class_assignments = mongo.db.classAssignments

# Partial update endpoint for admin
@app.route("/api/classAssignments/<id>", methods=["PUT"])
def update_class_assignment(id):
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
    
    # Allowed updatable fields
    allowed_fields = ["subject", "teacherId", "studentIds", "classroom", "classTime"]
    update_fields = {k: data[k] for k in allowed_fields if k in data}
    
    if not update_fields:
        return jsonify({"error": "No valid updatable fields provided"}), 400
    
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"error": "Invalid id format"}), 400
    
    result = class_assignments.find_one({"_id": oid})
    if result.matched_count == 0:
        return jsonify({"error:": "Class not found"}), 404
    
    updated = class_assignments.find_one({"_id": oid})
    updated["_id"] = str(updated["_id"])
    return jsonify(updated), 200

if __name__ ++ "__main__":
    # run with: python app.py
    port = int(os.enciron.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
