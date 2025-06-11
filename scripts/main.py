from scripts.google_api import GoogleAPI
from scripts.extract_data import YouTubeDataModel
from scripts.logger import logging
from scripts.load_data import *
from scripts.constants import PROJECT_ID, DATASET_ID

google_api = GoogleAPI()

api = google_api.get_service()

# List of multiple channel_ids
channel_ids = [
    "UCX6OQ3DkcsbYNE6H8uQQuVA", #Mr. Beast
    "UC4-79UOlP48-QNGgCko5p2g", #Mr. Beast2
    "UCbCmjCuTUZos6Inko4u57UQ", #cocomelon
    "UCk8GzjMOrta8yxDcKfylJYw", #kids diana show
    "UCRijo3ddMTht_IHyNSNXpNQ" #dude perfect
]

# Initialize the Youtube data model
yt_model = YouTubeDataModel(api_client=api, channel_ids=channel_ids)

# === Fetch Data and Save to Files ===
# ---------- Extraction process ----------
logging.info("Fetching Channel Data...")
yt_model.get_channel_stats()

logging.info("Fetching Playlist Data...")
yt_model.get_all_playlists()

logging.info("Fetching Video Data...")
yt_model.get_videos_from_playlist()

logging.info("✅ All data fetched and saved successfully.")

# ---------- Transformation process ---------
logging.info("Transformation of data")
yt_model.video_data = clean_datetime(yt_model.video_data, 'published_date')

logging.info("Cleaned and transformed the data")

# ----------- Loading process -------------
logging.info("Loading the data into BigQuery...")
#print(yt_model.channel_data.head())
upload_to_bigquery(yt_model.channel_data, 'channel_data', PROJECT_ID, DATASET_ID)
upload_to_bigquery(yt_model.playlist_data, 'playlist_data', PROJECT_ID, DATASET_ID)
upload_to_bigquery(yt_model.video_data, 'video_data', PROJECT_ID, DATASET_ID)

print("🚀 Full YouTube ETL pipeline completed.")