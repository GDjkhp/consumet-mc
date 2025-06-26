from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.megacloud.megacloud import Megacloud
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

__all__ = ("HiAnime",)


class HiAnime(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self) -> str:
        return "https://hianime.to"

    def _search_title(self, query: str, page: int) -> PagedResult:
        url = f"{self._base_url}/search/?keyword={query}&page={page}"
        return self._scrape_card_page(url)

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "most-popular":
            return self._scrape_most_popular(page)
        elif query.strip().lower() == "top-airing":
            return self._scrape_top_airing(page)
        elif query.strip().lower() == "most-favorite":
            return self._scrape_most_favorite(page)
        elif query.strip().lower() == "latest-completed":
            return self._scrape_latest_completed(page)
        elif query.strip().lower() == "recently-updated":
            return self._scrape_recently_updated(page)
        elif query.strip().lower() == "recently-added":
            return self._scrape_recently_added(page)
        elif query.strip().lower() == "subbed-anime":
            return self._scrape_subbed_anime(page)
        elif query.strip().lower() == "dubbed-anime":
            return self._scrape_dubbed_anime(page)
        elif query.strip().lower() == "movie":
            return self._scrape_movie(page)
        elif query.strip().lower() == "tv":
            return self._scrape_tv(page)

        return PagedResult()

    def _scrape_most_popular(self, page: int):
        url = f"{self._base_url}/most-popular?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_top_airing(self, page: int):
        url = f"{self._base_url}/top-airing?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_most_favorite(self, page: int):
        url = f"{self._base_url}/most-favorite?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_latest_completed(self, page: int):
        url = f"{self._base_url}/completed?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_recently_updated(self, page: int):
        url = f"{self._base_url}/recently-updated?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_recently_added(self, page: int):
        url = f"{self._base_url}/recently-added?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_subbed_anime(self, page: int):
        url = f"{self._base_url}/subbed-anime?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_dubbed_anime(self, page: int):
        url = f"{self._base_url}/dubbed-anime?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_movie(self, page: int):
        url = f"{self._base_url}/movie?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_tv(self, page: int):
        url = f"{self._base_url}/tv?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_card_page(self, url: str) -> PagedResult:
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=0)

            pagination = soup.select_one(".page-item.active")
            if pagination:
                current_page_tag = pagination.select_one(".page-item.active")
                next_page_tag = pagination.select_one("a[title=Next]")

                if current_page_tag:
                    paged_result.current_page = int(current_page_tag.text())
                if next_page_tag:
                    paged_result.has_next_page = (
                        True if "href" in next_page_tag else False
                    )
            paged_result.results = self._scrape_card(soup)
            if not paged_result.results:
                paged_result.current_page = 0
                paged_result.has_next_page = False

            return paged_result

        except Exception as e:
            raise e

    def _scrape_card(self, tag: Tag):
        metadatas: List[Metadata] = []

        for card in tag.select(".flw-item"):
            atag = cast(Tag, card.select_one(".film-name a"))
            id = cast(str, atag["href"]).split("/")[1].split("?")[0]
            title = atag.text
            image_url = cast(Tag, card.select_one("img"))["data-src"]
            metadatas.append(
                Metadata(id, title, MetadataType.MULTI, cast(str, image_url))
            )
        return metadatas

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            url = f"{self._base_url}/ajax/v2/episode/servers?episodeId={episode_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.json()["html"])

            server_tags = soup.select(".item.server-item")
            servers = []

            sub_or_dub = self.options.get("sub_or_dub", "sub")

            for server_tag in server_tags:
                server_name = (
                    str(cast(Tag, server_tag.select_one("a")).text).strip().lower()
                )
                data_id = cast(str, server_tag["data-id"])
                data_type = cast(str, server_tag["data-type"])

                # * megacloud -> HD-1 HD-2 HD-3

                if "hd" in server_name:
                    server_url = self._scrape_video_server_data(data_id)

                    if data_type == sub_or_dub:
                        servers.append(
                            VideoServer(
                                server_name,
                                server_url,
                                extra_data={
                                    "referer": self._base_url,
                                },
                            )
                        )
            return servers

        except Exception as e:
            raise e

    def _scrape_video_server_data(self, server_data_id: str):
        try:
            url = f"{self._base_url}/ajax/v2/episode/sources/?id={server_data_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            data = response.json()
            return data["link"]

        except Exception as e:
            raise e

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        return Megacloud(self.http_client, server)

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            url = f"{self._base_url}/ajax/v2/episode/list/{media_id.split('-')[-1]}"
            headers = {
                "X-Requested-with": "XMLHttpRequest",
                "Referer": f"{self._base_url}/watch/{media_id}",
            }
            response = self.http_client.request("GET", url, headers=headers)
            response.raise_for_status()

            soup = self.soup(
                response.json()["html"],
            )
            episodes: List[Episode] = []

            for tag in soup.select("div.detail-infor-content > div > a"):
                episode_id = cast(str, tag["data-id"])
                episode_number = int(cast(str, tag["data-number"]))

                episodes.append(Episode(episode_id, 1, episode_number))

            return episodes

        except Exception as e:
            raise e
