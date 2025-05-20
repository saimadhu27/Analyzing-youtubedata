from scripts.google_api import GoogleAPI
from scripts.extract_data import YouTubeDataModel

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
data_extraction = YouTubeDataModel(api_client=api, channel_ids=channel_ids)

# === Fetch Data and Save to Files ===
print("Fetching Channel Data...")
data_extraction.get_channel_stats()

print("Fetching Playlist Data...")
data_extraction.get_all_playlists()

print("Fetching Video Data...")
data_extraction.get_videos_from_playlist()

print("✅ All data fetched and saved successfully.")