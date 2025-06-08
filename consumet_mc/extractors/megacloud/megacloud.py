from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mov_cli.http_client import HTTPClient

from consumet_mc.extractors.video_extractor import (
    StreamingServer,
    Video,
    VideoExtractor,
    Subtitle,
)
from .megacloud_getsrcs import get_sources


class Megacloud(VideoExtractor):
    def __init__(self, http_client: HTTPClient) -> None:
        super().__init__(http_client)

    @property
    def server_name(self) -> StreamingServer:
        return StreamingServer.MEGACLOUD

    def extract(self, url: str, **kwargs) -> list[Video]:
        videos = []
        try:
            referer = str(kwargs["referer"])
            response = get_sources(url, referer)
            if response:
                sources = response["sources"]
                tracks = response["tracks"]
                video_url = sources[0]["file"]
                video_type = sources[0]["type"]
                is_m3u8 = True if "hls" in video_type else False
                subtitles = []

                for track in tracks:
                    if "label" in track:
                        subtitles.append(Subtitle(track["file"], track["label"]))
                videos.append(Video(video_url, is_m3u8, subtitles=subtitles))

            return videos

        except Exception as e:
            raise e
