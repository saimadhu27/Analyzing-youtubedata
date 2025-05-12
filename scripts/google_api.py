import os
import sys

from googleapiclient.discovery import build
from scripts.logger import logging
from scripts.exception import MyException
from scripts.constants import API_KEY, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION

class GoogleAPI:
    """
    GoogleAPI class to handle YouTube Data API v3 interactions.
    It initializes a connection with the API and handles exceptions gracefully.
    """
    def __init__(self):
        try:
            self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
            logging.info("YouTube API Connection Successful")
            
        except Exception as e:
            raise MyException(e, sys)

    def get_service(self):
        """
        Returns the YouTube API client instance.
        """
        return self.youtube