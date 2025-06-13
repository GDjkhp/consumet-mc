from __future__ import annotations

import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mov_cli.http_client import HTTPClient

from mov_cli.http_client import HTTPClient
from consumet_mc.utils.packer import unpack
from consumet_mc.extractors.video_extractor import (
    StreamingServer,
    Video,
    VideoExtractor,
    Subtitle,
)


class Kwik(VideoExtractor):
    def __init__(self, http_client: HTTPClient) -> None:
        super().__init__(http_client)

    @property
    def server_name(self) -> StreamingServer:
        return StreamingServer.BUILTIN

    def extract(self, url: str, **kwargs) -> list[Video]:
        videos = []
        try:
            referer = str(kwargs["referer"])
            headers = {"Referer": referer}
            response = self.http_client.request("GET", url, headers=headers)
            response.raise_for_status()
            decoded_source = unpack(response.text)
            if decoded_source:
                source_url_regex = r"source='([^']*)'"
                match = re.search(source_url_regex, decoded_source)
                if match:
                    source_url = match.group(1)
                    videos.append(
                        Video(source_url, True if ".m3u8" in source_url else False)
                    )
            return videos

        except Exception as e:
            raise e


# url = "https://kwik.si/e/X4fwYapNTuJ2"
#
# kwik = Kwik(HTTPClient())
# extracted = kwik.extract(url, referer="https://animepahe.ru/")
# print(extracted)
