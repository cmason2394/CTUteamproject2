from pymongo import MongoClient

class GradeManager:
def __init__(self, uri="mongodb://localhost:27017/", db_name="school_db"):
self.client = MongoClient(uri)
self.db = self.client[db_name]
self.students = self.db["students"] # Collection for student data

def add_student(self, student_id, name):
# Check if student already exists
if self.students.find_one({"student_id": student_id}):
print("Student already exists.")
return
self.students.insert_one({
"student_id": student_id,
"name": name,
"grades": {}
})
print(f"Student {name} added successfully.")

def record_grade(self, student_id, assignment, grade):
result = self.students.update_one(
{"student_id": student_id},
{"$set": {f"grades.{assignment}": grade}}
)
if result.matched_count > 0:
print(f"Grade recorded: {student_id} - {assignment}: {grade}")
else:
print("Student not found.")

def view_grades(self, student_id=None):
if student_id:
student = self.students.find_one({"student_id": student_id})
if student:
print(f"Grades for {student['name']}:")
for assignment, grade in student["grades"].items():
print(f" {assignment}: {grade}")
else:
print("Student not found.")
else:
for student in self.students.find():
print(f"\nGrades for {student['name']}:")
for assignment, grade in student["grades"].items():
print(f" {assignment}: {grade}")
