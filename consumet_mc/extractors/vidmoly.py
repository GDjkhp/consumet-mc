from __future__ import annotations

import re
from typing import cast


from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.source import Source
from consumet_mc.models.video import Video


class Vidmoly(VideoExtractor):
    def extract(self) -> Source:
        try:
            videos = []
            response = self.http_client.request(
                "GET", self.server.url, include_default_headers=True
            )
            response.raise_for_status()

            video_url_regex = r"file:\s*\"([^\"]+)\""
            video_url = str(
                cast(re.Match, re.search(video_url_regex, response.text)).group(1)
            )
            videos.append(Video(video_url, True if ".m3u8" in video_url else False))
            return Source(videos)

        except Exception as e:
            raise e
