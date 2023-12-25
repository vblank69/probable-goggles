from __future__ import unicode_literals
import yt_dlp as youtube_dl

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'default_search': 'auto',
    'logger': MyLogger(),
}

YTDL = youtube_dl.YoutubeDL(ydl_opts)

class Audio:
    def __init__(self, dixt):
        self.title = dixt.get('title')
        self.url = dixt.get('url')
        self.duration = dixt.get('duration')
        self.audio_loc = dixt.get('audio_loc')
        return None

    def get_source(self):
        return self.audio_loc

    @classmethod
    def extract_info(self, url):
        ie_result = YTDL.extract_info(url, False)
        if 'entries' in ie_result.keys():
            ie_result = ie_result['entries'][0]
        media_dict = {}
        media_dict['title'] = ie_result['title']
        media_dict['url'] = ie_result['original_url']
        media_dict['duration'] = ie_result['duration']
        media_dict['audio_loc'] = ie_result['url']
        return media_dict

if __name__ == "__main__":
    url = 'https://www.tiktok.com/@bmk.kkj/video/7274806562961624326'
    media_dict = Audio(url)
    #media_dict = ydl.extract_info(f"ytsearch:{url}", False)['entries'][0]
    print(media_dict.title)
