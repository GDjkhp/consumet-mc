from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Optional, List
    from mov_cli.http_client import HTTPClient

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

__all__ = ("Video", "VideoExtractor", "Subtitle")


@dataclass
class Subtitle:
    url: str
    lang: Optional[str] = field(default=None)


@dataclass
class Video:
    url: str
    is_m3u8: Optional[bool] = field(default=False)
    quality: Optional[str] = field(default=None)
    subtitles: Optional[List[Subtitle]] = field(default=None)


class StreamingServer(str, Enum):
    ASIANLOAD = "asianload"
    GOGOCDN = "gogocdn"
    STREAMSB = "streamsb"
    MIXDROP = "mixdrop"
    MP4UPLOAD = "mp4upload"
    UPCLOUD = "upcloud"
    VIDCLOUD = "vidcloud"
    STREAMTAPE = "streamtape"
    VIZCLOUD = "vizcloud"
    # same as vizcloud
    MYCLOUD = "mycloud"
    FILEMOON = "filemoon"
    VIDSTREAMING = "vidstreaming"
    BUILTIN = "builtin"
    SMASHYSTREAM = "smashystream"
    STREAMHUB = "streamhub"
    STREAMWISH = "streamwish"
    VIDHIDE = "vidhide"
    VIDMOLY = "vidmoly"
    VOE = "voe"
    MEGAUP = "megaup"
    KK = "kk"
    MEGACLOUD = "megacloud"
    KWIK = "kwik"
    ENGIFUOSI = "engifuosi"
    TUKIPASTI = "tukipasti"


class VideoExtractor(ABC):
    """A base class for building extractor from."""

    def __init__(self, http_client: HTTPClient) -> None:
        self.http_client = http_client

        super().__init__()

    @property
    @abstractmethod
    def server_name(self) -> StreamingServer:
        """the server name of the video provider"""

    @abstractmethod
    def extract(self, url: str, **kwargs) -> List[Video]:
        """where your extracting for video should be done. should return list of videos"""
        ...
