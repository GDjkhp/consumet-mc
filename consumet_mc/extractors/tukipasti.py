from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from mov_cli.http_client import HTTPClient

from mov_cli.http_client import HTTPClient
from consumet_mc.extractors.video_extractor import (
    StreamingServer,
    Video,
    VideoExtractor,
)


class Tukipasti(VideoExtractor):
    def __init__(self, http_client: HTTPClient) -> None:
        super().__init__(http_client)

    @property
    def server_name(self) -> StreamingServer:
        return StreamingServer.TUKIPASTI

    def extract(self, url: str, **kwargs) -> list[Video]:
        videos = []
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            source_url_regex = r"var urlPlay = '(.*?)'"
            source_url = str(
                cast(re.Match, re.search(source_url_regex, response.text)).group(1)
            )
            videos.append(Video(source_url, True if ".m3u8" in source_url else False))
            return videos

        except Exception as e:
            raise e
