#student.py

# import necessary libraries/modules/classes
from person import Person

class Student (Person):
    """
    Initializes a new student object, using the abstract person class as the base.

    Args:
        All from the persoon class: name, contact info, username, and password
        birth_date (date mm:dd:yyyy): student's birthday
        address (str): student's address
    """
    def __init__(self, name, contact_info, username, password, birth_date, address):
        # Call the parent class's __init__ method to inherit attributes
        super().__init__(name, contact_info, username, password)
        
        self.birth_date = birth_date
        self.address = address
        self.class_ids = [] # list to store class ids of classes student has taken
        self.grades = {} # dictionary to store grades

    def calculate_GPA():
        """
        Calculates a student's GPA based on their class grades of past and current classes

        Returns
        -------
        GPA

        """
        pass
