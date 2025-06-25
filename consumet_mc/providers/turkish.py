from __future__ import annotations

from re import Match
import re
from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.extractors.tukipasti import Tukipasti
from consumet_mc.extractors.engifuosi import Engifuosi
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

__all__ = ("Turkish",)


class Turkish(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self) -> str:
        return "https://turkish123.ac"

    def _search_title(self, query: str, page: int) -> PagedResult:
        url = f"{self._base_url}/wp-admin/admin-ajax.php?s={query}&action=searchwp_live_search&swpengine=default&swpquery={query}"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=0)

            li_tags = soup.select("li:not(.ss-bottom)")

            for li_tag in li_tags:
                id = (
                    str(cast(Tag, li_tag.select_one("a"))["href"])
                    .replace(self._base_url, "")
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

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "series-list":
            return self._scrape_series_list()

        return PagedResult()

    def _scrape_series_list(self):
        url = f"{self._base_url}/series-list/"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            ml_item_tags = soup.select(".movies-list.movies-list-full div.ml-item ")

            for ml_item_tag in ml_item_tags:
                id = (
                    str(cast(Tag, ml_item_tag.select_one("a"))["href"])
                    .replace(self._base_url, "")
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

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            url = f"{self._base_url}/{episode_id}/"

            response = self.http_client.request("GET", url)
            response.raise_for_status()

            tukipasti_regex = r"\"(https:\/\/tukipasti.com\/t\/.*?)\""
            engifuosi_regex = r"\"(https:\/\/engifuosi.com\/f\/.*?)\""

            tukipasti_match = re.search(tukipasti_regex, response.text)

            engifuosi_match = re.search(engifuosi_regex, response.text)

            servers = []

            if tukipasti_match:
                server_url = tukipasti_match.group(1)
                server_name = "tukipasti"
                servers.append(
                    VideoServer(
                        server_name, server_url, extra_data={"referer": self._base_url}
                    )
                )

            if engifuosi_match:
                server_url = engifuosi_match.group(1)
                server_name = "engifuosi"
                servers.append(
                    VideoServer(
                        server_name,
                        server_url,
                    )
                )

            return servers

        except Exception as e:
            raise e

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        if server.name == "tukipasti":
            return Tukipasti(self.http_client, server)
        elif server.name == "engifuosi":
            return Engifuosi(self.http_client, server)

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            episodes: List[Episode] = []

            url = f"{self._base_url}/{media_id}/"
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
