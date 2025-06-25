from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.streamwish import StreamWish
from consumet_mc.extractors.asianload import AsianLoad
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.video_server import VideoServer
from consumet_mc.utils.utils import USER_AGENT

from .provider import Provider

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

from mov_cli import Metadata, MetadataType

__all__ = ("DramaCool",)


class DramaCool(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self):
        return "https://dramacoolz.lv"

    def _search_title(self, query: str, page: int) -> PagedResult:
        url = f"{self._base_url}/page/{page}/?s={query}"
        url = f"{self._base_url}/?s={query}"
        try:
            # headers = {"User-Agent": USER_AGENT}
            headers = {"User-Agent": USER_AGENT, "Referer": url}
            response = self.http_client.request("GET", url, headers=headers)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            article_tags = soup.select(".result-item > article")

            for article_tag in article_tags:
                id = str(
                    cast(Tag, article_tag.select_one(".details .title > a"))["href"]
                ).replace(self._base_url, "")
                title = str(
                    cast(Tag, article_tag.select_one(".details .title > a")).text
                )
                image_url = str(
                    cast(Tag, article_tag.select_one(".image a > img "))["src"]
                )

                metadata_type = (
                    MetadataType.SINGLE if "movies" in id else MetadataType.MULTI
                )

                paged_result.results.append(
                    Metadata(id, title, metadata_type, image_url)
                )

            return paged_result
        except Exception as e:
            raise e

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "recent-drama":
            return self._scrape_recent_drama()
        elif query.strip().lower() == "recent-movies":
            return self._scrape_recent_movies()
        return PagedResult()

    def _scrape_recent_drama(self):
        url = f"{self._base_url}"
        try:
            headers = {"User-Agent": USER_AGENT}
            response = self.http_client.request("GET", url, headers=headers)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            li_tags = soup.select("#dt-episode .poster ")

            for li_tag in li_tags:
                id = str(cast(Tag, li_tag.select_one("a"))["href"]).replace(
                    self._base_url, ""
                )
                title = str(cast(Tag, li_tag.select_one("a > img"))["alt"])
                image_url = str(cast(Tag, li_tag.select_one("a > img"))["data-src"])

                paged_result.results.append(
                    Metadata(id, title, MetadataType.MULTI, image_url)
                )

            return paged_result

        except Exception as e:
            raise e

    def _scrape_recent_movies(self) -> PagedResult:
        url = f"{self._base_url}"
        try:
            headers = {"User-Agent": USER_AGENT}
            response = self.http_client.request("GET", url, headers=headers)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            article_tags = soup.select("#dt-movie > article")

            for article_tag in article_tags:
                id = str(
                    cast(Tag, article_tag.select_one(".poster > a"))["href"]
                ).replace(self._base_url, "")
                title = str(
                    cast(Tag, article_tag.select_one(".poster > a > img"))["alt"]
                )
                image_url = str(
                    cast(Tag, article_tag.select_one(".poster > a > img "))["data-src"]
                )

                paged_result.results.append(
                    Metadata(id, title, MetadataType.SINGLE, image_url)
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

            server_tags = soup.select("#playeroptionsul > li")

            servers = []

            for server_tag in server_tags:
                server_data_type = str(server_tag["data-type"])
                server_data_post = str(server_tag["data-post"])
                server_data_nume = str(server_tag["data-nume"])
                server_name = str(
                    cast(Tag, server_tag.select_one(".title")).text
                ).lower()

                server_url = self._scrape_video_server_data(
                    server_data_type, server_data_post, server_data_nume
                )

                servers.append(
                    VideoServer(
                        server_name, server_url, extra_data={"referer": self._base_url}
                    )
                )

            return servers

        except Exception as e:
            raise e

    def _scrape_video_server_data(self, data_type: str, data_post: str, data_nume: str):
        try:
            request_body = {
                "action": "doo_player_ajax",
                "post": data_post,
                "nume": data_nume,
                "type": data_type,
            }
            url = f"{self._base_url}/wp-admin/admin-ajax.php"

            headers = {"User-Agent": USER_AGENT}
            response = self.http_client.request(
                "POST", url, data=request_body, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data["embed_url"]
        except Exception as e:
            raise e

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        if server.name == "streamwish":
            return StreamWish(self.http_client, server)
        elif server.name == "standard server":
            return AsianLoad(self.http_client, server)

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            episodes: List[Episode] = []

            url = f"{self._base_url}{media_id}"
            headers = {"User-Agent": USER_AGENT, "Referer": self._base_url}
            response = self.http_client.request("GET", url, headers=headers)
            response.raise_for_status()

            soup = self.soup(response.text)

            li_tags = soup.select("#seasons .episodios > li")
            li_tags.reverse()

            for idx, tag in enumerate(li_tags):
                episode_id = str(cast(Tag, tag.select_one("a"))["href"]).replace(
                    self._base_url, ""
                )
                episode_number = idx + 1

                episodes.append(Episode(episode_id, 1, episode_number))

            return episodes

        except Exception as e:
            raise e
