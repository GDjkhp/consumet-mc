from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

from consumet_mc.models.video_server import VideoServer
from consumet_mc.models.source import Source


if TYPE_CHECKING:
    from mov_cli.http_client import HTTPClient

from abc import ABC, abstractmethod


class VideoExtractor(ABC):
    """A base class for building extractor from"""

    def __init__(self, http_client: HTTPClient, server: VideoServer) -> None:
        super().__init__()
        self.http_client = http_client
        self.server = server

    @abstractmethod
    def extract(self) -> Source:
        """where you are extracting sources"""
        ...
