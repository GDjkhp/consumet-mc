from __future__ import annotations

from re import Match
import re
from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.video_extractor import StreamingServer
from consumet_mc.extractors.tukipasti import Tukipasti
from consumet_mc.extractors.engifuosi import Engifuosi
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

__all__ = ("Turkish",)


class Turkish(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        self.base_url: str = "https://turkish123.ac"

        super().__init__(config, http_client, options)

    def search(self, query: str, limit: Optional[int] = None) -> List[Metadata]:
        limit = 1 if limit is None else limit
        page = cast(int, self.options.get("page", 1))
        search_mode = cast(str, self.options.get("mode", "title"))

        if search_mode == "title":
            return self._search(query, page).results
        elif search_mode == "category":
            if query.strip().lower() == "series-list":
                return self._scrape_series_list().results
            raise Exception("Unsupported query")
        else:
            raise Exception("Unsupported mode")

    def _search(self, query: str, page: int) -> PagedResult:
        url = f"{self.base_url}/wp-admin/admin-ajax.php?s={query}&action=searchwp_live_search&swpengine=default&swpquery={query}"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=0)

            li_tags = soup.select("li:not(.ss-bottom)")

            for li_tag in li_tags:
                id = (
                    str(cast(Tag, li_tag.select_one("a"))["href"])
                    .replace(self.base_url, "")
                    .replace("/", "")
                )
                title = str(cast(Tag, li_tag.select_one(".ss-title")).text)
                style = str(cast(Tag, li_tag.select_one("a"))["style"])
                image_url_regex = r"url\((.*?)\)"
                image_url = str(cast(Match, re.search(image_url_regex, style)).group(1))

                paged_result.results.append(
                    Metadata(id, title, MetadataType.MULTI, image_url)
                )

            return paged_result
        except Exception as e:
            raise e

    def _scrape_series_list(self):
        url = f"{self.base_url}/series-list/"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            ml_item_tags = soup.select(".movies-list.movies-list-full div.ml-item ")

            for ml_item_tag in ml_item_tags:
                id = (
                    str(cast(Tag, ml_item_tag.select_one("a"))["href"])
                    .replace(self.base_url, "")
                    .replace("/", "")
                )
                title = str(cast(Tag, ml_item_tag.select_one("a"))["oldtitle"])
                image_url = str(cast(Tag, ml_item_tag.select_one("img"))["src"])
                paged_result.results.append(
                    Metadata(id, title, MetadataType.MULTI, image_url)
                )
            return paged_result
        except Exception as e:
            raise e

    def scrape(
        self, metadata: Metadata, episode: EpisodeSelector
    ) -> Optional[Multi | Single]:
        server_name = self.options.get("server")

        episodes = self._scrape_episodes(metadata.id)
        selected_episode = episodes[-episode.episode]
        video_servers = self._scrape_video_servers(selected_episode.id, metadata.id)

        selected_video_server = None

        if server_name:
            for s in video_servers:
                if s.name == server_name:
                    selected_video_server = s
                    break
            if not selected_video_server:
                raise Exception(f"No video server found with name {server_name}")
        else:
            selected_video_server = video_servers[1]

        video_extractor = None
        if selected_video_server.name == StreamingServer.TUKIPASTI:
            video_extractor = Tukipasti(self.http_client)
        elif selected_video_server.name == StreamingServer.ENGIFUOSI:
            video_extractor = Engifuosi(
                self.http_client,
            )

        if video_extractor:
            videos = video_extractor.extract(
                selected_video_server.url, referer=self.base_url
            )
            if not videos:
                return None
            video = videos[0]

            if metadata.type == MetadataType.MULTI:
                return Multi(
                    video.url,
                    metadata.title,
                    episode,
                )
            else:
                return Single(video.url, metadata.title)
        return None

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            url = f"{self.base_url}/{episode_id}/"

            response = self.http_client.request("GET", url)
            response.raise_for_status()

            tukipasti_regex = r"\"(https:\/\/tukipasti.com\/t\/.*?)\""
            engifuosi_regex = r"\"(https:\/\/engifuosi.com\/f\/.*?)\""

            tukipasti_match = re.search(tukipasti_regex, response.text)

            engifuosi_match = re.search(engifuosi_regex, response.text)

            servers = []

            if tukipasti_match:
                server_url = tukipasti_match.group(1)
                server_name = StreamingServer.TUKIPASTI
                servers.append(
                    VideoServer(
                        server_name,
                        server_url,
                    )
                )

            if engifuosi_match:
                server_url = engifuosi_match.group(1)
                server_name = StreamingServer.ENGIFUOSI
                servers.append(
                    VideoServer(
                        server_name,
                        server_url,
                    )
                )

            return servers

        except Exception as e:
            raise e

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            episodes: List[Episode] = []

            url = f"{self.base_url}/{media_id}/"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)

            for idx, tag in enumerate(soup.select(".les-content > a")):
                episode_id = str(tag["href"]).split("/")[-2:][0]
                episode_number = idx + 1

                episodes.append(Episode(episode_id, 1, episode_number))

            return episodes

        except Exception as e:
            raise e

    def scrape_episodes(self, metadata: Metadata) -> ScrapeEpisodesT:
        if metadata.type == MetadataType.MULTI:
            scrape_episodes = {}
            episodes = self._scrape_episodes(metadata.id)
            scrape_episodes[1] = len(episodes)

            return scrape_episodes

        else:
            return {None: 1}
