# classtime.py

class Classtime:
    def __init__(self, start_time, end_time, start_date, end_date, weekdays): 
        """
        Initializes a new Classtime object.

        Args:
            start_time (time hh:mm): When the class starts for the day
            end_time (time hh:mm): When the class ends for the day
            start_date (date dd:mm:yy): First day of class for the session/semester
            end_date (date dd:mm:yy): Last day of class for the session/semester
            weekdays (list): Days of week when the class runs
        """
        self._id = None  # Will be populated by the database upon creation
        self.start_time = start_time
        self.end_time = end_time
        self.start_date = start_date
        self.end_date = end_date
        self.weekdays = weekdays

