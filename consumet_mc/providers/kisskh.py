from __future__ import annotations

from re import error
from typing import TYPE_CHECKING, cast

from consumet_mc.extractors.kk import KK
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult

from ..models import VideoServer
from .provider import Provider

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScrapeEpisodesT, ScraperOptionsT
    from mov_cli.utils import EpisodeSelector

from mov_cli import Metadata, MetadataType, Multi, Single

__all__ = ("Kisskh",)


class Kisskh(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        self.base_url: str = "https://kisskh.do/api"

        super().__init__(config, http_client, options)

    def search(self, query: str, limit: Optional[int] = None) -> List[Metadata]:
        limit = 1 if limit is None else limit
        page = cast(int, self.options.get("page", 1))
        search_mode = cast(str, self.options.get("mode", "title"))

        if search_mode == "title":
            return self._search(query, page).results
        elif search_mode == "category":
            if query.strip().lower() == "popular":
                return self._scrape_popular(page).results
            elif query.strip().lower() == "ongoing":
                return self._scrape_ongoing(page).results
            elif query.strip().lower() == "completed":
                return self._scrape_completed(page).results
            elif query.strip().lower() == "movie":
                return self._scrape_movies(page).results
            elif query.strip().lower() == "tv":
                return self._scrape_tv_series(page).results
            else:
                raise Exception("Unsupported query")
        else:
            raise Exception("Unsupported mode")

    def _search(self, query: str, page: int) -> PagedResult:
        url = f"{self.base_url}/DramaList/Search?q={query}"
        return self._scrape_metadata(url, page)

    def _scrape_popular(self, page: int):
        url = f"{self.base_url}/DramaList/List?page={str(page)}&type=0&order=1"
        return self._scrape_metadata(url, page)

    def _scrape_ongoing(self, page: int):
        url = f"{self.base_url}/DramaList/List?page={str(page)}&type=0&order=1&status=1"
        return self._scrape_metadata(url, page)

    def _scrape_completed(self, page: int):
        url = f"{self.base_url}/DramaList/List?page={str(page)}&type=0&order=1&status=2"
        return self._scrape_metadata(url, page)

    def _scrape_movies(self, page: int):
        url = f"{self.base_url}/DramaList/List?page={str(page)}&type=2&order=1&status=0"
        return self._scrape_metadata(url, page)

    def _scrape_tv_series(self, page: int):
        url = f"{self.base_url}/DramaList/List?page={str(page)}&type=1&order=1&status=0"
        return self._scrape_metadata(url, page)

    def _scrape_metadata(self, url: str, page: int) -> PagedResult:
        try:
            response = self.http_client.request("GET", url)
            response = response.raise_for_status()

            data = response.json()
            paged_result = PagedResult(current_page=page, total_pages=page)
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

    def scrape(
        self, metadata: Metadata, episode: EpisodeSelector
    ) -> Optional[Multi | Single]:
        episodes = self._scrape_episodes(metadata.id)
        selected_episode = episodes[-episode.episode]
        video_servers = self._scrape_video_servers(selected_episode.id)
        video_server = video_servers[0]

        if video_server.name == "kk":
            video_extractor = KK(self.http_client)
            videos = video_extractor.extract(
                video_server.embed,
                subs_url=video_server.extra_data["subs_url"],
                episode_id=video_server.extra_data["episode_id"],
            )
            video = videos[0]
            subtitles = None
            if video.subtitles:
                subtitles = list(map(lambda x: x.url, video.subtitles))
            return Multi(
                video.url,
                metadata.title,
                episode,
                subtitles=subtitles,
                referrer=self.base_url,
            )
        return None

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        episode_url = f"{self.base_url}/DramaList/Episode/{episode_id}.png"
        subs_url = f"{self.base_url}/Sub/{episode_id}"

        return [
            VideoServer(
                "kk",
                episode_url,
                extra_data={"subs_url": subs_url, "episode_id": episode_id},
            )
        ]

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[int] = None
    ) -> List[Episode]:
        try:
            extra_metadata_url = f"{self.base_url}/DramaList/Drama/{media_id}"
            response = self.http_client.request("GET", extra_metadata_url)
            response.raise_for_status()
            extra_metadata = response.json()

            episodes: List[Episode] = []

            for idx, ep in enumerate(extra_metadata["episodes"]):
                episodes.append(Episode(ep["id"], 1, idx))

            return episodes

        except error as e:
            raise e

    def scrape_episodes(self, metadata: Metadata) -> ScrapeEpisodesT:
        episodes = self._scrape_episodes(metadata.id)

        return {1: len(episodes)}
