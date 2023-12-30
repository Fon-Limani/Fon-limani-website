# UserPortfolio Class

from datetime import datetime
from typing import List

class UserPortfolio:
    def __init__(
        self,
        id: int,
        timestamp: datetime,
        funds: List[str],
        portions: List[int]
    ):
        """
        Initialize a UserPortfolio object.

        Parameters:
        - id (int): The unique identifier for the user portfolio.
        - timestamp (datetime): The timestamp of when the user portfolio was created.
        - funds (List[str]): List of fund codes associated with the user portfolio.
        - portions (List[int]): List of portions corresponding to each fund in the portfolio.
        """
        self.id = id
        self.timestamp = timestamp
        self.funds = funds
        self.portions = portions

    def __repr__(self) -> str:
        """
        Return a string representation of the UserPortfolio object.

        Returns:
        - str: String representation of the UserPortfolio.
        """
        return (
            f"UserPortfolio(id={repr(self.id)}, timestamp={repr(self.timestamp)}, "
            f"funds={repr(self.funds)}, portions={repr(self.portions)})"
        )