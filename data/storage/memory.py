import dataclasses
import os
import pathlib
from typing import NamedTuple

import dotenv
import yt_dlp
from yt_dlp import YoutubeDL

from data.storage.constants import max_reults

dotenv.load_dotenv()

PATH_VIDEO = pathlib.Path(os.getenv("PATH_VIDEO"))

PATH_AUDIO = pathlib.Path(os.getenv("PATH_AUDIO"))


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

        return list_urls, list_names, search_results

    def get_download(self, uuid, user_id):
        url = self.user_state[user_id].search_callbacks[uuid].url
        name_video = uuid
        options = {
            "format": "bestaudio/best",
            "outtmpl": str(PATH_AUDIO / f"{name_video}"),
            "ffmpeg_location": "/usr/bin/ffmpeg",
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

    def get_download_url(self, url, name_video):

        options = {
            "format": "bestaudio/best",
            "outtmpl": str(PATH_AUDIO / f"{name_video}"),
            "ffmpeg_location": "/usr/bin/ffmpeg",
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

    def get_video(self, url, user_id, uuid):
        if user_id not in self.user_state:
            self.user_state[user_id] = UserState(
                search_callbacks={}, video_callbacks={}
            )
        self.user_state[user_id].video_callbacks[uuid] = url
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get("formats", [])
            resolutions = set()
            for fmt in formats:
                if fmt.get("vcodec") != "none":
                    resolution = fmt.get("height")
                    if resolution:
                        resolutions.add(f"{resolution}")

        return resolutions

    def get_download_video(self, get_resolution, uuid, user_id):
        global format_id
        ydl_opts = {"quiet": True}
        url = self.user_state[user_id].video_callbacks[uuid]
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
        for fmt in formats:
            resolution = fmt.get("height", "unknown")
            if str(resolution) == str(get_resolution):
                try:
                    filesize = int(fmt.get("filesize", "unknown")) / 1000000
                except ValueError:
                    continue
                if float(filesize) >= 2000:
                    return "Размер файла больше 2000мб"
                else:
                    format_id = fmt.get("format_id")

        name_video = uuid
        ydl_opts = {
            "format": f"{format_id}",
            "outtmpl": str(PATH_VIDEO / f"{name_video}"),
            "nooverwrites": False,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        return name_video
