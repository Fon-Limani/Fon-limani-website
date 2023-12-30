from datetime import datetime
from typing import Optional

class Fund:
    def __init__(
        self,
        id: int,
        timestamp: datetime,
        history: str,
        fund_code: str,
        fund_title: str,
        umbrella_fund_type: str,
        price: float,
        fund_total_value: float,
        num_investors: int,
        portions: int
    ):
        """
        Initialize a Fund object.

        Parameters:
        - id (int): The unique identifier for the fund.
        - timestamp (datetime): The timestamp of when the fund was created.
        - history (str): The history of the fund.
        - fund_code (str): The code associated with the fund.
        - fund_title (str): The title or name of the fund.
        - umbrella_fund_type (str): The type of umbrella fund.
        - price (float): The price of the fund.
        - fund_total_value (float): The total value of the fund.
        - num_investors (int): The number of investors in the fund.
        - portions (int): The number of portions of the fund.
        """
        self.id = id
        self.timestamp = timestamp
        self.history = history
        self.fund_code = fund_code
        self.fund_title = fund_title
        self.umbrella_fund_type = umbrella_fund_type
        self.price = price
        self.fund_total_value = fund_total_value
        self.num_investors = num_investors
        self.portions = portions

    def __repr__(self) -> str:
        """
        Return a string representation of the Fund object.

        Returns:
        - str: String representation of the Fund.
        """
        return (
            f"Fund(id={repr(self.id)}, timestamp={repr(self.timestamp)}, "
            f"history={repr(self.history)}, fund_code={repr(self.fund_code)}, "
            f"fund_title={repr(self.fund_title)}, umbrella_fund_type={repr(self.umbrella_fund_type)}, "
            f"price={repr(self.price)}, fund_total_value={repr(self.fund_total_value)}, "
            f"num_investors={repr(self.num_investors)}, portions={repr(self.portions)})"
        )