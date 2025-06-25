from __future__ import annotations

from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.video import Video
from consumet_mc.models.source import Source


class Builtin(VideoExtractor):
    def extract(self) -> Source:
        videos = []
        videos.append(
            Video(self.server.url, True if ".m3u8" in self.server.url else False)
        )
        return Source(videos)
