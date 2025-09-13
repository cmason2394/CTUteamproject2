# classroom.py

class Classroom:
    def __init__(self, number): 
        """
        Initializes a new Classroom object.

        Args:
            number (str): The classroom number.
        """
        self._id = None  # Will be populated by the database upon creation
        self.number = number

