from __future__ import annotations

from typing import TYPE_CHECKING, cast

from mov_cli.media import Metadata, MetadataType, Multi, Single
from mov_cli.scraper import Scraper
from mov_cli.utils import EpisodeSelector

from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.season import Season
from consumet_mc.models.video_server import VideoServer

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT
    from mov_cli.scraper import ScrapeEpisodesT

from abc import ABC, abstractmethod


class Provider(Scraper, ABC):
    """A base class for building scrapers from."""

    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: Optional[ScraperOptionsT] = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    @abstractmethod
    def _base_url(self) -> str:
        """base url of provider"""

    @abstractmethod
    def _search_title(self, query: str, page: int) -> PagedResult:
        """
        search for media by title
        """
        ...

    def _search_category(self, query: str, page: int) -> PagedResult:
        """
        search for media by category
        """
        return PagedResult()

    def _search_genre(self, query: str, page: int) -> PagedResult:
        """
        search for media by genre
        """
        return PagedResult()

    @abstractmethod
    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> List[VideoServer]:
        """
        Where your scraping for episode video servers should be
        """
        ...

    def _scrape_seasons(self, media_id) -> List[Season]:
        """
        Where your scraping for season should be
        """
        return []

    @abstractmethod
    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        """
        Where your scraping for episodes should be
        """
        ...

    @abstractmethod
    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        """
        return a video extractor for a specific video server
        """
        ...

    def search(self, query: str, limit: Optional[int] = None) -> List[Metadata]:
        page = self.options.get("page", 1)
        page = int(page)
        search_mode = cast(str, self.options.get("mode", "title"))

        if search_mode == "title":
            return self._search_title(query, page).results
        elif search_mode == "category":
            return self._search_category(query, page).results
        elif search_mode == "genre":
            return self._search_genre(query, page).results
        else:
            raise Exception("Unsupported mode")

    def scrape_episodes(self, metadata: Metadata) -> ScrapeEpisodesT:
        season_episodes = {}
        seasons = self._scrape_seasons(metadata.id)
        if seasons:
            for season in seasons:
                episodes = self._scrape_episodes(metadata.id, season.id)
                season_episodes[season.season_number] = len(episodes)
        else:
            episodes = self._scrape_episodes(metadata.id)
            season_episodes[1] = len(episodes)

        return season_episodes

    def scrape(
        self, metadata: Metadata, episode: EpisodeSelector
    ) -> Optional[Multi | Single]:
        server_name = self.options.get("server")

        seasons = self._scrape_seasons(metadata.id)
        if seasons:
            seasons.reverse()
            season_id = seasons[-episode.season].id
            episodes = self._scrape_episodes(metadata.id, season_id)
        else:
            episodes = self._scrape_episodes(metadata.id)

        episodes.reverse()
        selected_episode = episodes[-episode.episode]

        video_servers = self._scrape_video_servers(selected_episode.id, metadata.id)
        if not video_servers:
            return

        selected_video_server = None
        if server_name:
            for s in video_servers:
                if s.name == str(server_name).lower():
                    selected_video_server = s
                    break
            if not selected_video_server:
                raise Exception(f"No video server found with name {server_name}")
        else:
            selected_video_server = video_servers[0]

        video_extractor = self._get_video_extractor(selected_video_server)
        if not video_extractor:
            return

        source = video_extractor.extract()
        if not source.videos:
            return None

        video = source.videos[0]
        subtitles = None
        if source.subtitles:
            subtitles = list(map(lambda x: x.url, source.subtitles))
        if metadata.type == MetadataType.MULTI:
            return Multi(
                video.url,
                metadata.title,
                episode,
                subtitles=subtitles,
                referrer=source.headers.get("referer", self._base_url),
            )
        else:
            return Single(
                video.url,
                metadata.title,
                subtitles=subtitles,
                referrer=source.headers.get("referer", self._base_url),
            )
