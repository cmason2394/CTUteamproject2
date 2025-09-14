#administrator.py

# import necessary libraries/modules/classes
from person import Person

class Administrator (Person):
    """
    Initializes a new administrator object, using the abstract person class as the base.

    Args:
        All the same as the persoon class: name, contact info, username, and password
    """
    def __init__(self, name, contact_info, username, password):
        # Call the parent class's __init__ method to inherit attributes
        super().__init__(name, contact_info, username, password)

    def assign_student_to_class(self, class_id, student_ids):
        """
        Assigns a student to a class while checking for limits and conflicts.
        
        This method will contain the core logic for the user story, including:
        - Verifying class capacity (20 student limit).
        - Checking for scheduling conflicts for each student.
        - Updating the class roster and student schedules in the database.
        - Handling exceptions and displaying success/error messages.
        """
        # TODO: Implement this method based on the acceptance criteria and task list.
        
        
        pass
