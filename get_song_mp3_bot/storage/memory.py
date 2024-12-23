import dataclasses
import re
from typing import NamedTuple

import yt_dlp
from yt_dlp import YoutubeDL

from get_song_mp3_bot.storage.constants import max_reults


class SearchResult(NamedTuple):
    url: str
    name: str


@dataclasses.dataclass
class SearchCallbackData:
    links: dict[str, SearchResult]


@dataclasses.dataclass
class VideoResCallbackData:
    links: list[str]


@dataclasses.dataclass
class UserState:
    search_callbacks: dict[str, SearchCallbackData]
    video_callbacks: dict[str, VideoResCallbackData]


class MemoryList:

    def __init__(self):
        self.user_state: dict[int, UserState] = {}

    def get_urls(self, querty, user_id):
        max_result = max_reults
        ydl_opts = {"format": "bestaudio", "noplaylist": True, "quiet": True}

        # Use ytsearch to perform the search
        search_term = f"ytsearch{max_result }:{querty}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(search_term, download=False)
        list_urls = [
            video["webpage_url"] for video in search_results.get("entries", [])
        ]
        list_names = [video["title"] for video in search_results.get("entries", [])]
        search_results = []

        for i in range(len(list_names)):
            search_results.append(SearchResult(url=list_urls[i], name=list_names[i]))

        if user_id not in self.user_state:
            self.user_state[user_id] = UserState(
                search_callbacks={}, video_callbacks={}
            )

        print(list_urls, list_names)
        return list_urls, list_names, search_results

    def get_download(self, uuid, user_id):
        name_video = self.user_state[user_id].search_callbacks[uuid].name
        url = self.user_state[user_id].search_callbacks[uuid].url
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

    # def get_download_url(self, url):
    #     ydl_opts = {"quiet": True}
    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         info_dict = ydl.extract_info(url, download=False)
    #         video_title = info_dict.get("title", None)
    #     name_video = re.sub(r'[\\/*?:"<>|]', "", video_title)
    #     options = {
    #         "format": "bestaudio/best",
    #         "outtmpl": f"./youtube_audio/{name_video}.%(ext)s",
    #         "ffmpeg_location": "C:/ffmpeg/bin",
    #         "postprocessors": [
    #             {
    #                 "key": "FFmpegExtractAudio",
    #                 "preferredcodec": "mp3",
    #                 "preferredquality": "192",
    #             }
    #         ],
    #     }
    #
    #     with YoutubeDL(options) as ydl:
    #         ydl.download([url])
    #     return name_video
    #
    # def get_videoe(self, url):
    #     ydl_opts = {"quiet": True}  # Отключить вывод
    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         info_dict = ydl.extract_info(url, download=False)
    #         formats = info_dict.get("formats", [])
    #         resolutions = set()  # Используем множество, чтобы исключить дубли
    #
    #         for fmt in formats:
    #             if fmt.get("vcodec") != "none":  # Только форматы с видеокодеком
    #                 resolution = fmt.get("height")
    #                 if resolution:  # Проверяем, что разрешение существует
    #                     resolutions.add(f"{resolution}p")
    #
    #     return resolutions
