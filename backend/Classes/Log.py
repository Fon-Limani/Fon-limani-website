from datetime import datetime

class Log:
    def __init__(
        self,
        id: int,
        timestamp: datetime,
        error_code: int,
        error_message: str
    ):
        """
        Initialize a Log object.

        Parameters:
        - id (int): The unique identifier for the log.
        - timestamp (datetime): The timestamp of when the log was created.
        - error_code (int): The error code associated with the log.
        - error_message (str): The error message/details.
        """
        self.id = id
        self.timestamp = timestamp
        self.error_code = error_code
        self.error_message = error_message

    def __repr__(self) -> str:
        """
        Return a string representation of the Log object.

        Returns:
        - str: String representation of the Log.
        """
        return (
            f"Log(id={repr(self.id)}, timestamp={repr(self.timestamp)}, "
            f"error_code={repr(self.error_code)}, error_message={repr(self.error_message)})"
        )