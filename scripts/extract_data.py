import os
import sys
import pandas as pd
from datetime import datetime

from scripts.google_api import GoogleAPI
from scripts.logger import logging
from scripts.exception import MyException

# ====== Directory Setup =====
BASE_DIR = "data"
CHANNELS_DIR = os.path.join(BASE_DIR, "channels")
PLAYLISTS_DIR = os.path.join(BASE_DIR, "playlists")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

# Create directories if they don't exist
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(CHANNELS_DIR, exist_ok=True)
os.makedirs(PLAYLISTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)


class YouTubeDataModel:
    """YouTubeDataModel is a data handler for You Tube API data.
    It fetches and organizes data into three main categories:
    1. Channel data
    2. Playlist data
    3. Video data
    All data is stored in pandas DataFrames for easy processing and analysis.
    """
    def __init__(self, api_client, channel_ids):
        """Initializes the YouTubeData object.

        Args:
            api_client (_type_): Google API client object initialized for YouTube.
            channel_id (str): The unique ID of the YouTube channel
        """
        self.api_client = api_client
        self.channel_ids = channel_ids
        
        # DataFrames for the three main entities
        self.channel_data = pd.DataFrame()
        self.playlist_data = pd.DataFrame()
        self.video_data = pd.DataFrame()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def get_channel_stats(self):
        """Fetches the main statistics of the YouTube Channel.

        Returns:
            parquet : a parquet file that contains basic channel information.
        """
        all_channels = []
        
        for channel_id in self.channel_ids:
            try:
                # API Request to get channel details
                request = self.api_client.channels().list(
                    part="snippet,contentDetails,statistics",
                    id=channel_id
                )
                response = request.execute()

                #Parse the response
                if response['items']:
                    item = response['items'][0]
                    all_channels.append({
                        'channel_id': channel_id,
                        'channel_name': item['snippet']['title'],
                        'subscribers': item['statistics'].get('subscriberCount', 0),
                        'total_views': item['statistics'].get('viewCount', 0),
                        'video_count': item['statistics'].get('videoCount', 0)
                    })

                    logging.info(f"Channel data fetched successfully for {item['snippet']['title']}")
            
                else:
                    logging.warning("No channel data found.")
        
            except Exception as e:
                raise MyException(e, sys)
            
        # Store in DataFrame and save to Parquet
        self.channel_data = pd.DataFrame(all_channels)
        filename = f"{self.today}_channel_data.csv"
        self.channel_data.to_csv(os.path.join(CHANNELS_DIR, filename), index = False)
        logging.info(f"Channel data saved to {filename}")
        
    def get_all_playlists(self):
        """Fetches all playlists associated with the channel.

        Returns:
         parquet : returns a parquet file with all playlist ids, playlist name and each playlist video count within a channel.
        """
        playlist_records = []
        
        for channel_id in self.channel_ids:
            next_page_token = None
            try:
                while True:
                    request = self.api_client.playlists().list(
                        part="snippet,contentDetails",
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token
                    )
                    response = request.execute()
                
                    for item in response['items']:
                        playlist_records.append({
                            'playlist_id': item['id'],
                            'playlist_title': item['snippet']['title'],
                            'channel_id': channel_id,
                            'video_count': item['contentDetails']['itemCount']
                        })
                
                    next_page_token = response.get('nextPageToken')
                    if not next_page_token:
                        break
                
                logging.info(f"Fetched playlists for the channel : {channel_id}")

            except Exception as e:
                raise MyException(e, sys)
        # Store in DataFrame and save to Parquet
        self.playlist_data = pd.DataFrame(playlist_records)
        filename = f"{self.today}_playlist_data.csv"
        self.playlist_data.to_csv(os.path.join(PLAYLISTS_DIR, filename), index = False) 
        logging.info(f"Playlist data saved to {filename}")       
        
    def get_videos_from_playlist(self):
        """Fetches all videos from each playlist retrieved in the pervious step.
        Returns:
         parquet : returns a parquet file with all video information for all playlists within that channel.
        """
        all_videos = []
        
        
        #Iterate through each playlist and fetch videos
        for _, playlist in self.playlist_data.iterrows():
            playlist_id = playlist['playlist_id']
            next_page_token = None
            video_ids = []
            try:
                #Fetch all video IDs from the playlist
                while True:
                    request = self.api_client.playlistItems().list(
                        part='contentDetails',
                        playlistId=playlist_id,
                        maxResults=50,
                        pageToken=next_page_token
                    )
                    response = request.execute()
                
                    video_ids.extend([
                        item['contentDetails']['videoId'] for item in response['items']
                    ])
                    next_page_token = response.get('nextPageToken')
                
                    if not next_page_token:
                        break
                
                # Fetch video statistics in batches of 50
                for i in range(0, len(video_ids), 50):
                    request = self.api_client.videos().list(
                        part='snippet,statistics',
                        id=','.join(video_ids[i:i+50])
                    )
                    response = request.execute()
                    
                    # Parse and collect video statistics
                    for video in response['items']:
                        all_videos.append({
                            'video_id': video['id'],
                            'video_title': video['snippet']['title'],
                            'published_date': video['snippet']['publishedAt'],
                            'views': video['statistics'].get('viewCount', 0),
                            'likes': video['statistics'].get('likeCount', 0),
                            'comments': video['statistics'].get('commentCount', 0),
                            'playlist_id': playlist_id
                        })
                logging.info(f"Fetched {len(video_ids)} videos from playlist: {playlist_id}")
                
            except Exception as e:
                raise MyException(e, sys)
            
        # Store in DataFrame and save to Parquet
        self.video_data = pd.DataFrame(all_videos)
        filename = f"{self.today}_video_data.csv"
        self.video_data.to_csv(os.path.join(VIDEOS_DIR, filename), index = False)
        #self.video_data.to_parquet(os.path.join(VIDEOS_DIR, filename), index = False)
        logging.info(f"Video data saved to {filename}")
                
# def get_channel_info(channel_id):
#     try:
#         request = youtube.channels().list(
#             part="snippet,statistics",
#             id=channel_id
#         )
#         response = request.execute()
#         return response
#     except Exception as e:
#         raise MyException(e, sys)
   
# # Run the example
# if __name__ == "__main__":
#     CHANNEL_ID = "UCYO_jab_esuFRV4b17AJtAw"  # 3Blue1Brown
#     response = get_channel_stats(CHANNEL_ID)
#     print(response) 