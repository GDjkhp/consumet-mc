from __future__ import annotations

from typing import TYPE_CHECKING

from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.video_server import VideoServer

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

from abc import ABC, abstractmethod

from mov_cli.scraper import Scraper

__all__ = ("Provider",)


class Provider(Scraper, ABC):
    """A base class for building scrapers from."""

    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: Optional[ScraperOptionsT] = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @abstractmethod
    def _search(self, query: str, page: int) -> PagedResult:
        """
        search for media
        """
        ...

    @abstractmethod
    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> List[VideoServer]:
        """
        Where your scraping for episode video servers should be
        """
        ...

    @abstractmethod
    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        """
        Where your scraping for episodes should be
        """
        ...
