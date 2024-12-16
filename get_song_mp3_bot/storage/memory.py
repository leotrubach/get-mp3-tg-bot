import re

import yt_dlp
from yt_dlp import YoutubeDL


class MemoryList:

    def __init__(self):
        self.urls_list = {}

        # user_id : video_name
        self.url_name_video = {}

    def get_urls(self, querty, user_id):
        max_results = 3
        ydl_opts = {"format": "best", "noplaylist": True, "quiet": True}

        # Use ytsearch to perform the search
        search_term = f"ytsearch{max_results}:{querty}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(search_term, download=False)
        self.urls_list[user_id] = [
            video["webpage_url"] for video in search_results.get("entries", [])
        ]
        self.url_name_video[user_id] = [
            video["title"] for video in search_results.get("entries", [])
        ]

        return self.urls_list[user_id], self.url_name_video[user_id]

    def get_download(self, num, user_id):
        url = self.urls_list[user_id][num - 1]
        name_video = self.url_name_video[user_id][num - 1]
        name_video = re.sub(r'[\\/*?:"<>|]', "", name_video)
        options = {
            "format": "bestaudio/best",
            "outtmpl": f"./youtube_audio/{name_video}.%(ext)s",
            "ffmpeg_location": "C:/ffmpeg/bin",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with YoutubeDL(options) as ydl:
            ydl.download([url])
        return name_video

    def get_download_url(self, url):
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get("title", None)
        name_video = re.sub(r'[\\/*?:"<>|]', "", video_title)
        options = {
            "format": "bestaudio/best",
            "outtmpl": f"./youtube_audio/{name_video}.%(ext)s",
            "ffmpeg_location": "C:/ffmpeg/bin",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with YoutubeDL(options) as ydl:
            ydl.download([url])
        return name_video
