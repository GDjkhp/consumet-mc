from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bs4 import Tag

from consumet_mc.extractors import voe
from consumet_mc.extractors.filemoon import Filemoon
from consumet_mc.extractors.voe import Voe
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.season import Season
from consumet_mc.models.video_server import VideoServer
from consumet_mc.utils.utils import USER_AGENT

from .provider import Provider

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

from mov_cli import Metadata, MetadataType


class AniWorld(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self):
        return "https://aniworld.to"

    def _search_title(self, query: str, page: int) -> PagedResult:
        try:
            url = f"{self._base_url}/ajax/search"
            headers = {"User-Agent": USER_AGENT, "X-Requested-With": "XMLHttpRequest"}
            request_data = {"keyword": query}
            response = self.http_client.request(
                "POST", url, headers=headers, data=request_data
            )
            response.raise_for_status()

            data = response.json()
            paged_result = PagedResult()
            for i in data:
                paged_result.results.append(
                    Metadata(i["link"], i["title"], MetadataType.MULTI)
                )

            return paged_result
        except Exception as e:
            raise e

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "popular-anime":
            return self._scrape_popular_anime()
        return PagedResult()

    def _scrape_popular_anime(self):
        try:
            url = f"{self._base_url}/beliebte-animes"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)
            div_tags = soup.select(".seriesListContainer.row > div")
            paged_result = PagedResult()
            for tag in div_tags:
                title = str(cast(Tag, tag.select_one("a"))["title"])
                id = str(cast(Tag, tag.select_one("a"))["href"])
                img_url = str(cast(Tag, tag.select_one("a > img"))["data-src"])
                img_url = f"{self._base_url}{img_url}"
                paged_result.results.append(
                    Metadata(
                        id,
                        title,
                        MetadataType.MULTI,
                        img_url,
                    )
                )

            return paged_result
        except Exception as e:
            raise e

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            url = f"{self._base_url}{episode_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)

            sub_or_dub = self.options.get("sub_or_dub", "sub")
            selected_language = None
            language_tags = soup.select(".changeLanguageBox  img")
            for tag in language_tags:
                language_title = str(tag["title"])
                data_lang_key = str(tag["data-lang-key"])
                if sub_or_dub == "sub" and language_title == "mit Untertitel Deutsch":
                    selected_language = data_lang_key
                    break
                elif sub_or_dub == "dub" and language_title == "Deutsch":
                    selected_language = data_lang_key
                    break

            if not selected_language:
                return []

            server_tags = soup.select(".hosterSiteVideo .row > li")
            servers = []

            for server_tag in server_tags:
                data_lang_key = cast(str, server_tag["data-lang-key"])
                if data_lang_key != selected_language:
                    continue

                server_url_redirect = str(cast(Tag, server_tag.select_one("a"))["href"])
                server_url_redirect = f"{self._base_url}{server_url_redirect}"
                response = self.http_client.request("GET", server_url_redirect)
                if not response.has_redirect_location:
                    continue
                server_url = response.headers["location"]
                server_name = (
                    str(cast(Tag, server_tag.select_one("a > i"))["title"])
                    .split()[-1]
                    .lower()
                )
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
        if server.name == "filemoon":
            return Filemoon(self.http_client, server)
        elif server.name == "voe":
            return Voe(self.http_client, server)

    def _scrape_seasons(self, media_id: str):
        try:
            url = f"{self._base_url}/{media_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)
            li_tags = soup.select("#stream ul:first-child > li:not(:first-child)")
            seasons: List[Season] = []
            for idx, tag in enumerate(li_tags):
                title = str(cast(Tag, tag.select_one("a"))["title"])
                id = str(cast(Tag, tag.select_one("a"))["href"])
                seasons.append(Season(id, idx + 1, title))

            return seasons
        except Exception as e:
            raise e

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            url = f"{self._base_url}{season_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            episodes: List[Episode] = []
            soup = self.soup(response.text)
            td_tags = soup.select(".seasonEpisodesList > tbody > tr")

            for idx, tag in enumerate(td_tags):
                id = str(cast(Tag, tag.select_one("a"))["href"])
                episodes.append(Episode(id, 0, idx + 1))

            return episodes

        except Exception as e:
            raise e
