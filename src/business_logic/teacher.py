#teacher.py

# import necessary libraries/modules/classes
from person import Person

class Teacher (Person):
    """
    Initializes a new teacher object, using the abstract person class as the base.

    Args:
        All from the persoon class: name, contact info, username, and password
        qualifications (list): list of certifications and subjects the teacher is qualified to teach
    """
    def __init__(self, name, contact_info, username, password, qualifications):
        # Call the parent class's __init__ method to inherit attributes
        super().__init__(name, contact_info, username, password)
        
        self.qualifications = qualifications
