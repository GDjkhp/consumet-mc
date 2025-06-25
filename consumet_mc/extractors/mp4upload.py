from __future__ import annotations

import re
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.source import Source
from consumet_mc.models.video import Video


class Mp4Upload(VideoExtractor):
    def extract(self) -> Source:
        videos = []
        try:
            response = self.http_client.request("GET", self.server.url, redirect=True)
            response.raise_for_status()
            video_url_regex = r"(?<=player\.src\()\s*{\s*type:\s*\"[^\"]+\",\s*src:\s*\"([^\"]+)\"\s*}\s*(?=\);)"

            match = re.search(video_url_regex, response.text)
            if match:
                video_url = match.group(1)
                videos.append(Video(video_url, True if ".m3u8" in video_url else False))

            source = Source(videos)
            source.headers["Referer"] = "https://www.mp4upload.com/"

            return source

        except Exception as e:
            raise e
