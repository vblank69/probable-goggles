import math
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .youtube import Audio, YTDL

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
client_credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials)

class Spotify(Audio):
    def __init__(self, dixt):
        self.title = dixt.get('name')
        self.url = dixt.get('external_urls').get('spotify')
        self.duration = Spotify.transform_duration(dixt.get('duration_ms'))
        self.audio_loc = None
        self._search = f'{self.title} - {dixt.get("artist")}'
        return None

    def get_source(self):
        if self.audio_loc is not None:
            ie_result = YTDL.extract_info(self._search, False)
            self.audio_loc = ie_result.get('url')
        return self.audio_loc

    @classmethod
    def extract_info(_, url: str = None):
        result = None
        start = url.find('https://open.spotify.com/')
        if start > -1:
            start = url.find('/track/')
            if start > -1:
                end = url.find('?')
                track_id = url[start + 7 : end]
                result = sp.track(track_id=track_id)
            start = url.find('/playlist/')
            if start > -1:
                end = url.find('?')
                playlist_id = url[start + 10 : end]
                result = sp.playlist(playlist_id=playlist_id)
            start = url.find('/artist/')
            if start > -1:
                end = url.find('?')
                artist_id = url[start + 8 : end]
                result = sp.artist(artist_id=artist_id)
            start = url.find('/album/')
            if start > -1:
                end = url.find('?')
                album_id = url[start + 7 : end]
                result = sp.album(album_id=album_id)
        return result
    
    @classmethod
    def transform_duration(self, duration_ms: int = 0):
        minutes = math.floor(duration_ms / 60e3)
        duration_ms = duration_ms - minutes
        seconds = math.floor(duration_ms / 1e3)
        return f'{minutes}:{seconds}'
