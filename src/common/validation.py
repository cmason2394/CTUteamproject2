def validate_teacher_not_double_booked(teacher, class_):
  for assigned_class in teacher.assigned_classes:
    if assigned_class.time == class_.time:
      raise ValueError(
        f"Teacher {teacher.name} is already assigned "
        f"to a class at {class_.time}"
      )
