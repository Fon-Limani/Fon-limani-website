from datetime import datetime

class Message:
    def __init__(
        self,
        id: int,
        timestamp: datetime,
        title: str,
        body: str,
        email: str
    ):
        """
        Initialize a Message object.

        Parameters:
        - id (int): The unique identifier for the message.
        - title (str): The title of the message.
        - body (str): The body or content of the message.
        - from_id (str): The unique identifier of the sender.
        - from_name (str): The name of the sender.
        - to_id (str): The unique identifier of the recipient.
        - to_name (str): The name of the recipient.
        - deleted (bool, optional): Whether the message is marked as deleted (default is False).
        - hidden_for_sender (bool, optional): Whether the message is hidden for the sender (default is False).
        """
        self.id = id
        self.timestamp = timestamp
        self.title = title
        self.body = body
        self.email = email

    def __repr__(self) -> str:
        """
        Return a string representation of the Message object.

        Returns:
        - str: String representation of the Message.
        """
        return (
            f"Message(id={repr(self.id)}, title={repr(self.title)}, "
            f"body={repr(self.body)}, from_id={repr(self.from_id)}, "
            f"email={repr(self.email)}, "
        )
