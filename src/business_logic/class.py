# class.py

# import necessary libraries/modules/classes
from teacher import Teacher
from classroom import Classroom
from classtime import Classtime


class Class:
    def __init__(self, name, subject, teacher_id, classroom: Classroom, classtime: Classtime): 
        """
        Initializes a new Class object.

        Args:
            name (str): The class's name, such as "Python Programming".
            subject (str): the class's subject, such as "Computer Science".
            teacher_id (int): The ID of the teacher assigned to the class.
            classroom (Classroom): An instance of the Classroom class.
            classtime (Classtime): An instance of the Classtime class.
        """
        self._id = None  # Will be populated by the database upon creation
        self.name = name
        self.subject = subject
        self.teacher_id = teacher_id
        self.classroom = classroom
        self.classtime = classtime
        self.student_ids = []  # A list to store student IDs for a class roster
        self.max_size = 20     # The student limit per class
