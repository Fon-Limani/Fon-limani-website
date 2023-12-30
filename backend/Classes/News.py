# News Class

from datetime import datetime

class News:
    def __init__(
        self,
        id: int,
        timestamp: datetime,
        news_title: str,
        news_information: str,
        news_keywords: str,
        news_effects: str
    ):
        """
        Initialize a News object.

        Parameters:
        - id (int): The unique identifier for the news.
        - timestamp (datetime): The timestamp of when the news was created.
        - news_title (str): The title of the news.
        - news_information (str): Information/details about the news.
        - news_keywords (str): Keywords associated with the news.
        - news_effects (str): Effects or impact of the news.
        """
        self.id = id
        self.timestamp = timestamp
        self.news_title = news_title
        self.news_information = news_information
        self.news_keywords = news_keywords
        self.news_effects = news_effects

    def __repr__(self) -> str:
        """
        Return a string representation of the News object.

        Returns:
        - str: String representation of the News.
        """
        return (
            f"News(news_id={repr(self.id)}, timestamp={repr(self.timestamp)}, "
            f"news_title={repr(self.news_title)}, news_information={repr(self.news_information)}, "
            f"news_keywords={repr(self.news_keywords)}, news_effects={repr(self.news_effects)})"
        )