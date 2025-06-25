from __future__ import annotations

import re

from consumet_mc.models.source import Source
from consumet_mc.utils.packer import unpack
from consumet_mc.utils.utils import USER_AGENT
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.video import Video


class StreamWish(VideoExtractor):
    def extract(self) -> Source:
        videos = []
        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.9,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "*",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "max-age=0",
                "Priority": "u=0, i",
                "Referer": self.server.extra_data["referer"],
                "Origin": self.server.extra_data["referer"],
                "Sec-Ch-Ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "Linux",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": USER_AGENT,
                "Connection": "Keep-alive",
            }
            response = self.http_client.request("GET", self.server.url, headers=headers)
            response.raise_for_status()
            decoded_source = unpack(response.text)

            if decoded_source:
                video_url_regex = r"https?:\/\/[^\"]+?\.m3u8[^\"]*"
                match = re.search(video_url_regex, decoded_source)
                if match:
                    video_url = match.group(0)
                    videos.append(
                        Video(video_url, True if ".m3u8" in video_url else False)
                    )
            return Source(videos)

        except Exception as e:
            raise e
