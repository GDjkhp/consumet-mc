from __future__ import annotations

import base64
import re

from consumet_mc.models.source import Source
from consumet_mc.models.video import Video
from consumet_mc.utils.packer import unpack
from consumet_mc.utils.utils import USER_AGENT
from consumet_mc.extractors.video_extractor import VideoExtractor


class AsianLoad(VideoExtractor):
    def extract(self) -> Source:
        videos = []
        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.9,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": self.server.extra_data["referer"],
                "User-Agent": USER_AGENT,
                "Connection": "Keep-alive",
            }
            response = self.http_client.request(
                "GET", self.server.url, headers=headers, redirect=True
            )

            response.raise_for_status()
            decoded_source = unpack(response.text)

            if decoded_source:
                video_url_regex = r"window\.atob\([\"\']([^\"\']+)[\"\']\)"
                match = re.search(video_url_regex, decoded_source)
                if match:
                    video_url = match.group(1)
                    video_url = base64.b64decode(video_url).decode("utf-8")
                    videos.append(
                        Video(video_url, True if ".m3u8" in video_url else False)
                    )
            return Source(videos)

        except Exception as e:
            raise e
