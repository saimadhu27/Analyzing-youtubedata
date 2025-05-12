import os
import sys
import pandas as pd

from scripts.google_api import GoogleAPI
from scripts.logger import logging
from scripts.exception import MyException

#Initialize the API
# api = GoogleAPI()

# youtube = api.get_service()


class YouTubeDataModel:
    def __init__(self, api_client, channel_id):
        self.api_client = api_client
        self.channel_id = channel_id
        
        # D
        
    def get_channel_stats(self):
        """Fetches the main statistics of the YouTube Channel.

        Returns:
            dict : a dictionary that contains basic channel information.
        """
        try:
            request = self.api_client.channels().list(
            part="snippet,contentDetails,statistics",
            id=self.channel_id
            )
            response = request.execute()
        
            if response['items']:
                item = response['items'][0]
                self.channel_data = {
                    'Channel_name': item['snippet']['title'],
                    'Subscribers': item['statistics'].get('subscriberCount', 0),
                    'Total_views': item['statistics'].get('viewCount', 0),
                    'Video_count': item['statistics'].get('videoCount', 0)
                    #'Playlist_id': item['contentDetails']['relatedPlaylists']['uploads']
                }
                #self.playlist_id = item['contentDetails']['relatedPlaylists']['uploads']
                logging.info(f"Channel data fetched successfully for {self.channel_data['Channel Title']}")
            
            else:
                logging.warning("No channel data found.")
            return self.channel_data
        
        except Exception as e:
            raise MyException(e, sys)
        
    def get_all_playlists(self):
        """Fetches all playlists associated with the channel.

        Returns:
         pd.DataFrame : returns a dataframe with all playlist ids, playlist name and each playlist video count within a channel.
        """
        self.playlist_data = []
        next_page_token = None
        try:
            while True:
                request = self.api_client.playlists().list(
                    part="snippet,contentDetails",
                    channelId=self.channel_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response['items']:
                    self.playlist_data.append({
                        'Playlist_title': item['snippet']['title'],
                        'Playlist_id': item['id'],
                        'Video_count': item['contentDetails']['itemCount']
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
            logging.info(f"Fetched {len(self.playlist_data)} playlists for the channel.")
            return pd.DataFrame(self.playlist_data)
        except Exception as e:
            raise MyException(e, sys)
        
        
class YouTubeVideo:
    def __init__(self, api_client):
        self.api_client = api_client
        
    def get_videos_ids_from_playlist(self, playlist_id):
        """Fetches all video IDs from a playlist

        Args:
            playlist_id (str): the id of a single playlist
        """
        video_ids = []
        next_page_token = None
        try:
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
            logging.info(f"Fetched {len(video_ids)} videos from playlist: {playlist_id}")
        
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
   
# Run the example
if __name__ == "__main__":
    CHANNEL_ID = "UCYO_jab_esuFRV4b17AJtAw"  # 3Blue1Brown
    response = get_channel_stats(CHANNEL_ID)
    print(response) 