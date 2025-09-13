from .teacher import Teacher
from .class import class
from ..common import validation

class Assignment:
  def __init__ (self, teacher: Teacher, class_: Class):
    # Validate teacher availability, not double booked.
    validation.validate_teacher_not_double_booked(teacher, class_)

    self.teacher = teacher
    self.class_ = class_
  def to_dict(self):
    return {
      "teacher_id": self.teacher.teacher_id,
      "class_id": self.class_.class_id
    }
