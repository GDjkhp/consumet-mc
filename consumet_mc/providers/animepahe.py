from __future__ import annotations

from typing import TYPE_CHECKING, cast

from consumet_mc.extractors.kwik import Kwik
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

__all__ = ("AnimePahe",)


class AnimePahe(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self):
        return "https://animepahe.ru"

    def _search_title(self, query: str, page: int) -> PagedResult:
        try:
            url = f"{self._base_url}/api?m=search&q={query}&{str(page)}"
            response = self.http_client.request("GET", url, headers=self._headers())
            response.raise_for_status()

            data = response.json()
            paged_result = PagedResult()
            for i in data["data"]:
                paged_result.results.append(
                    Metadata(
                        i["session"],
                        i["title"],
                        MetadataType.MULTI
                        if i["type"] == "TV"
                        else MetadataType.SINGLE,
                        i["poster"],
                    )
                )

            return paged_result
        except Exception as e:
            raise e

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "latest-releases":
            return self._scrape_latest_releases(page)
        return PagedResult()

    def _scrape_latest_releases(self, page: int):
        try:
            url = f"{self._base_url}/api?m=airing&page={str(page)}"
            response = self.http_client.request("GET", url, headers=self._headers())
            response.raise_for_status()

            data = response.json()
            paged_result = PagedResult()
            for i in data["data"]:
                paged_result.results.append(
                    Metadata(
                        i["anime_session"],
                        i["anime_title"],
                        MetadataType.MULTI,
                        i["snapshot"],
                    )
                )

            return paged_result
        except Exception as e:
            raise e

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            url = f"{self._base_url}/play/{media_id}/{episode_id}"
            response = self.http_client.request(
                "GET", url, headers=self._headers(episode_id)
            )
            response.raise_for_status()

            soup = self.soup(response.text)

            server_tags = soup.select("div#resolutionMenu > button")
            servers = []

            sub_or_dub = self.options.get("sub_or_dub", "sub")
            for server_tag in server_tags:
                server_url = cast(str, server_tag["data-src"])
                server_audio = cast(str, server_tag["data-audio"])
                if "kwik.si" in server_url:
                    if "eng" in server_audio:
                        if sub_or_dub == "dub":
                            servers.append(
                                VideoServer(
                                    "kwik",
                                    server_url,
                                    extra_data={"referer": self._base_url},
                                )
                            )
                    else:
                        if sub_or_dub == "sub":
                            servers.append(
                                VideoServer(
                                    "kwik",
                                    server_url,
                                    extra_data={"referer": self._base_url},
                                )
                            )

            return servers

        except Exception as e:
            raise e

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        if server.name == "kwik":  # Builtin
            return Kwik(self.http_client, server)

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            current_page = 1
            episodes: List[Episode] = []
            while True:
                url = f"{self._base_url}/api?m=release&id={media_id}&sort=episode_asc&page={str(current_page)}"
                response = self.http_client.request(
                    "GET", url, headers=self._headers(media_id)
                )
                response.raise_for_status()

                data = response.json()

                for item in data["data"]:
                    episodes.append(Episode(item["session"], 1, item["episode"]))

                if data["current_page"] == data["last_page"]:
                    break
                current_page += 1

            return episodes

        except Exception as e:
            raise e

    def _headers(self, id: Optional[str] = None):
        return {
            "authority": "animepahe.ru",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "cookie": "__ddg2_=;",
            "dnt": "1",
            "sec-ch-ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"{self._base_url}/anime/{id}" if id else self._base_url,
        }
