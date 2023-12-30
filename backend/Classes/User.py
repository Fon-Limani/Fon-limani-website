from datetime import datetime, timedelta
from typing import Optional

class User:
    def __init__(
        self,
        id: int,
        timestamp: datetime,
        first_name: str,
        last_name: str,
        username: str,
        password: bytes,
        email: str,
        verified: bool = False,
        subscription: bool = False,
        subscription_end_date: datetime = None
    ):
        """
        Initialize a User object.

        Parameters:
        - id (int): The unique identifier for the user.
        - title (str): The title of the user (e.g., Mr, Mrs, Dr).
        - first_name (str): The first name of the user.
        - last_name (str): The last name of the user.
        - email (str): The email address of the user.
        - verified (bool, optional): Whether the user's email is verified (default is False).
        - subscription (bool, optional): Whether the user has a subscription (default is False).
        - subscription_end_date (datetime, optional): The end date of the user's subscription (default is None).
        """
        self.id = id
        self.timestamp = timestamp
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.email = email
        self.verified = verified
        self.subscription = subscription
        self.subscription_end_date = subscription_end_date

        # If subscription_end_date is not provided, set it to None
        if subscription_end_date is None and subscription:
            self.subscription_end_date = self._calculate_default_subscription_end_date()

    def _calculate_default_subscription_end_date(self) -> datetime:
        """
        Calculate the default end date for a subscription (30 days from the current date).

        Returns:
        - datetime: The calculated default end date.
        """
        return datetime.now() + timedelta(days=30)

    def __repr__(self) -> str:
        """
        Return a string representation of the User object.

        Returns:
        - str: String representation of the User.
        """
        return (
            f"User(id={repr(self.id)}, title={repr(self.title)}, "
            f"first_name={repr(self.first_name)}, last_name={repr(self.last_name)}, username={repr(self.username)}, "
            f"email={repr(self.email)}, verified={repr(self.verified)}, "
            f"subscription={repr(self.subscription)}, "
            f"subscription_end_date={repr(self.subscription_end_date)})"
        )