import os
from dotenv import load_dotenv

#Load environment variables from .env file
load_dotenv()

#YouTube API
API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#BigQuery
PROJECT_ID="youtube-analytics-459121"
DATASET_ID="youtube_data"