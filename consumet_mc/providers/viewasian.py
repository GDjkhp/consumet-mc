from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.vidmoly import Vidmoly
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

__all__ = ("ViewAsian",)


class ViewAsian(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self) -> str:
        return "https://viewasian.lol"

    def _search_title(self, query: str, page: int) -> PagedResult:
        url = f"{self._base_url}/page/{page}/?type=movies&s={query}"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            li_tags = soup.select(".list-episode-item > li")

            for li_tag in li_tags:
                id = str(cast(Tag, li_tag.select_one("a"))["href"]).replace(
                    self._base_url, ""
                )
                title = str(cast(Tag, li_tag.select_one("a"))["title"])
                image_url = str(cast(Tag, li_tag.select_one("a > img"))["src"])

                paged_result.results.append(
                    Metadata(id, title, MetadataType.MULTI, image_url)
                )

            return paged_result
        except Exception as e:
            raise e

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "most-popular-drama":
            return self._scrape_most_popular_drama(page)
        elif query.strip().lower() == "recent-drama":
            return self._scrape_recent_drama()

        return PagedResult()

    def _scrape_most_popular_drama(self, page: int):
        url = f"{self._base_url}/most-popular-drama/page/{page}/"
        try:
            response = self.http_client.request("GET", url, redirect=True)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            li_tags = soup.select(".content-left .block-tab .list-episode-item > li")

            for li_tag in li_tags:
                id = str(cast(Tag, li_tag.select_one("a"))["href"]).replace(
                    self._base_url, ""
                )
                title = str(cast(Tag, li_tag.select_one("a"))["title"])
                image_url = str(cast(Tag, li_tag.select_one("a > img"))["src"])

                paged_result.results.append(
                    Metadata(id, title, MetadataType.MULTI, image_url)
                )

            return paged_result

        except Exception as e:
            raise e

    def _scrape_recent_drama(self):
        url = f"{self._base_url}/"
        try:
            response = self.http_client.request("GET", url, redirect=True)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            li_tags = soup.select(".content-left .selected .list-episode-item > li")

            for li_tag in li_tags:
                id = str(cast(Tag, li_tag.select_one("a"))["href"]).replace(
                    self._base_url, ""
                )
                title = str(cast(Tag, li_tag.select_one("a > img"))["title"])
                image_url = str(
                    cast(Tag, li_tag.select_one("a > img"))["data-original"]
                )

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

            soup = self.soup(response.text)

            standard_server = str(
                cast(Tag, soup.select_one(".Standard.Server.selected"))["data-video"]
            )

            servers = []
            if "kisskh" in standard_server:
                url = standard_server
                response = self.http_client.request("GET", url, redirect=True)
                soup = self.soup(response.text)

                server_tags = soup.select(".list-server-items > li")

                for server_tag in server_tags:
                    server_url = str(server_tag["data-video"])
                    server_name = str(server_tag["data-provider"])
                    servers.append(
                        VideoServer(
                            server_name,
                            server_url,
                            extra_data={"referer": self._base_url},
                        )
                    )
            elif "vidmoly" in standard_server:
                server_url = standard_server
                server_name = "vidmoly"
                servers.append(
                    VideoServer(
                        server_name,
                        server_url,
                        extra_data={"referer": self._base_url},
                    )
                )

            return servers

        except Exception as e:
            raise e

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        if server.name == "vidmoly":
            return Vidmoly(self.http_client, server)

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            episodes: List[Episode] = []

            url = f"{self._base_url}{media_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)

            li_tags = soup.select(".all-episode > li")
            li_tags.reverse()

            for idx, tag in enumerate(li_tags):
                episode_id = (
                    str(cast(Tag, tag.select_one("a"))["href"])
                    .rstrip("/")
                    .rsplit("/", 1)[-1]
                )
                episode_number = idx + 1

                episodes.append(Episode(episode_id, 1, episode_number))

            return episodes

        except Exception as e:
            raise e
