from __future__ import annotations

from re import error
from typing import TYPE_CHECKING

from consumet_mc.extractors.kk import KK
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.video_server import VideoServer

from .provider import Provider

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

from mov_cli import Metadata, MetadataType

__all__ = ("Kisskh",)


class Kisskh(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self) -> str:
        return "https://kisskh.do/api"

    def _search_title(self, query: str, page: int) -> PagedResult:
        url = f"{self._base_url}/DramaList/Search?q={query}"
        return self._scrape_metadata(url, page)

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "popular":
            return self._scrape_popular(page)
        elif query.strip().lower() == "ongoing":
            return self._scrape_ongoing(page)
        elif query.strip().lower() == "completed":
            return self._scrape_completed(page)
        elif query.strip().lower() == "movie":
            return self._scrape_movies(page)
        elif query.strip().lower() == "tv":
            return self._scrape_tv_series(page)

        return PagedResult()

    def _scrape_popular(self, page: int):
        url = f"{self._base_url}/DramaList/List?page={str(page)}&type=0&order=1"
        return self._scrape_metadata(url, page)

    def _scrape_ongoing(self, page: int):
        url = (
            f"{self._base_url}/DramaList/List?page={str(page)}&type=0&order=1&status=1"
        )
        return self._scrape_metadata(url, page)

    def _scrape_completed(self, page: int):
        url = (
            f"{self._base_url}/DramaList/List?page={str(page)}&type=0&order=1&status=2"
        )
        return self._scrape_metadata(url, page)

    def _scrape_movies(self, page: int):
        url = (
            f"{self._base_url}/DramaList/List?page={str(page)}&type=2&order=1&status=0"
        )
        return self._scrape_metadata(url, page)

    def _scrape_tv_series(self, page: int):
        url = (
            f"{self._base_url}/DramaList/List?page={str(page)}&type=1&order=1&status=0"
        )
        return self._scrape_metadata(url, page)

    def _scrape_metadata(self, url: str, page: int) -> PagedResult:
        try:
            response = self.http_client.request("GET", url)
            response = response.raise_for_status()

            data = response.json()
            paged_result = PagedResult(current_page=page)
            if isinstance(data, dict):
                data = data["data"]

            for item in data:
                paged_result.results.append(
                    Metadata(
                        id=item["id"],
                        title=item["title"].strip(),
                        type=MetadataType.MULTI,
                        image_url=item["thumbnail"],
                    )
                )
            return paged_result

        except error as e:
            raise e

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        episode_url = f"{self._base_url}/DramaList/Episode/{episode_id}.png"
        subs_url = f"{self._base_url}/Sub/{episode_id}"

        return [
            VideoServer(
                "kk",
                episode_url,
                extra_data={"subs_url": subs_url, "episode_id": episode_id},
            )
        ]

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        return KK(self.http_client, server)

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            extra_metadata_url = f"{self._base_url}/DramaList/Drama/{media_id}"
            response = self.http_client.request("GET", extra_metadata_url)
            response.raise_for_status()
            extra_metadata = response.json()

            episodes: List[Episode] = []

            for idx, ep in enumerate(extra_metadata["episodes"]):
                episodes.append(Episode(ep["id"], 1, idx))

            return episodes

        except error as e:
            raise e
