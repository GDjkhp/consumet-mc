from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.megacloud.megacloud import Megacloud
from consumet_mc.extractors.upcloud import Upcloud
from consumet_mc.extractors.vidcloud import Vidcloud
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.extractors.vidzcloud import Vidzcloud
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.season import Season
from consumet_mc.models.video_server import VideoServer

from .provider import Provider

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

from mov_cli import Metadata, MetadataType


class HiMovies(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)

    @property
    def _base_url(self) -> str:
        return "https://himovies.sx"

    def _search_title(self, query: str, page: int) -> PagedResult:
        query = query.replace(" ", "-")
        url = f"{self._base_url}/search/{query}?page={page}"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=0)

            flw_item_tags = soup.select(".film_list-wrap > div.flw-item")

            for flw_item_tag in flw_item_tags:
                release_data = cast(
                    Tag,
                    flw_item_tag.select_one(
                        "div.film-detail > div.fd-infor > span:nth-child(1)"
                    ),
                ).text
                id = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > a"))["href"]
                )
                title = str(
                    cast(Tag, flw_item_tag.select_one("div.film-detail > h2 > a"))[
                        "title"
                    ]
                )
                image_url = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > img"))[
                        "data-src"
                    ]
                )

                media_type = str(
                    cast(
                        Tag,
                        flw_item_tag.select_one(
                            "div.film-detail > div.fd-infor > span.float-right"
                        ),
                    ).text
                )

                metadata_type = (
                    MetadataType.SINGLE if media_type == "Movie" else MetadataType.MULTI
                )

                paged_result.results.append(
                    Metadata(id, title, metadata_type, image_url, year=release_data)
                )

            return paged_result
        except Exception as e:
            raise e

    def _search_category(self, query: str, page: int) -> PagedResult:
        if query.strip().lower() == "recent-movies":
            return self._scrape_recent_movies()
        elif query.strip().lower() == "trending-movies":
            return self._scrape_trending_movies()
        elif query.strip().lower() == "trending-tv-shows":
            return self._scrape_trending_tv_shows()
        return PagedResult()

    def _scrape_recent_movies(self):
        url = f"{self._base_url}/home"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=0)

            flw_item_tags = soup.select(
                "section.block_area:contains('Latest Movies') > div:nth-child(2) > div:nth-child(1) > div.flw-item"
            )

            for flw_item_tag in flw_item_tags:
                release_data = cast(
                    Tag,
                    flw_item_tag.select_one(
                        "div.film-detail > div.fd-infor > span:nth-child(1)"
                    ),
                ).text
                id = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > a"))["href"]
                )
                title = str(
                    cast(Tag, flw_item_tag.select_one("div.film-detail > h3 > a"))[
                        "title"
                    ]
                )
                image_url = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > img"))[
                        "data-src"
                    ]
                )

                media_type = str(
                    cast(
                        Tag,
                        flw_item_tag.select_one(
                            "div.film-detail > div.fd-infor > span.float-right"
                        ),
                    ).text
                )

                metadata_type = (
                    MetadataType.SINGLE if media_type == "Movie" else MetadataType.MULTI
                )

                paged_result.results.append(
                    Metadata(
                        id,
                        title,
                        metadata_type,
                        image_url,
                        release_data,
                    )
                )
            return paged_result
        except Exception as e:
            raise e

    def _scrape_trending_movies(self):
        url = f"{self._base_url}/home"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            flw_item_tags = soup.select(
                "div#trending-movies div.film_list-wrap div.flw-item"
            )

            for flw_item_tag in flw_item_tags:
                release_data = cast(
                    Tag,
                    flw_item_tag.select_one(
                        "div.film-detail > div.fd-infor > span:nth-child(1)"
                    ),
                ).text
                id = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > a"))["href"]
                )
                title = str(
                    cast(Tag, flw_item_tag.select_one("div.film-detail > h3 > a"))[
                        "title"
                    ]
                )
                image_url = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > img"))[
                        "data-src"
                    ]
                )

                media_type = str(
                    cast(
                        Tag,
                        flw_item_tag.select_one(
                            "div.film-detail > div.fd-infor > span.float-right"
                        ),
                    ).text
                )

                metadata_type = (
                    MetadataType.SINGLE if media_type == "Movie" else MetadataType.MULTI
                )

                paged_result.results.append(
                    Metadata(
                        id,
                        title,
                        metadata_type,
                        image_url,
                        release_data,
                    )
                )
            return paged_result
        except Exception as e:
            raise e

    def _scrape_trending_tv_shows(self):
        url = f"{self._base_url}/home"
        try:
            response = self.http_client.request("GET", url)
            response.raise_for_status()
            soup = self.soup(response.text)

            paged_result = PagedResult(current_page=1)

            flw_item_tags = soup.select(
                "div#trending-tv div.film_list-wrap div.flw-item"
            )

            for flw_item_tag in flw_item_tags:
                release_data = cast(
                    Tag,
                    flw_item_tag.select_one(
                        "div.film-detail > div.fd-infor > span:nth-child(1)"
                    ),
                ).text
                id = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > a"))["href"]
                )
                title = str(
                    cast(Tag, flw_item_tag.select_one("div.film-detail > h3 > a"))[
                        "title"
                    ]
                )
                image_url = str(
                    cast(Tag, flw_item_tag.select_one("div.film-poster > img"))[
                        "data-src"
                    ]
                )

                media_type = str(
                    cast(
                        Tag,
                        flw_item_tag.select_one(
                            "div.film-detail > div.fd-infor > span.float-right"
                        ),
                    ).text
                )

                metadata_type = (
                    MetadataType.SINGLE if media_type == "Movie" else MetadataType.MULTI
                )

                paged_result.results.append(
                    Metadata(
                        id,
                        title,
                        metadata_type,
                        image_url,
                        release_data,
                    )
                )
            return paged_result
        except Exception as e:
            raise e

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            if media_id is None:
                return []

            if "movie" not in media_id:
                url = f"{self._base_url}/ajax/episode/servers/{episode_id}"
            else:
                url = f"{self._base_url}/ajax/episode/list/{episode_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)

            server_tags = soup.select(".nav > li")
            servers = []

            for server_tag in server_tags:
                data_id = str(cast(Tag, server_tag.select_one("a"))["data-id"])
                server_name = (
                    str(cast(Tag, server_tag.select_one("a"))["title"])[6:]
                    .strip()
                    .lower()
                )
                server_url = self._scrape_video_server_data(data_id)
                servers.append(
                    VideoServer(
                        server_name, server_url, extra_data={"referer": self._base_url}
                    )
                )

            return servers

        except Exception as e:
            raise e

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        if server.name == "upcloud":
            return Upcloud(self.http_client, server)
        elif server.name == "vidcloud":
            return Vidcloud(self.http_client, server)
        elif server.name == "akcloud":
            return Vidzcloud(self.http_client, server)
        # elif server.name == "megacloud":
        #     return Megacloud(self.http_client, server)

    def _scrape_video_server_data(self, server_data_id: str):
        try:
            url = f"{self._base_url}/ajax/episode/sources/{server_data_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            data = response.json()
            return data["link"]

        except Exception as e:
            raise e

    def _scrape_seasons(self, media_id) -> List[Season]:
        try:
            url = f"{self._base_url}/ajax/season/list/{media_id.split('-')[-1]}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)

            seasons = []

            for idx, season_id_tag in enumerate(soup.select(".dropdown-menu > a")):
                season_id = str(season_id_tag["data-id"])
                season_number = idx + 1
                seasons.append(Season(season_id, season_number))
            return seasons
        except Exception as e:
            raise e

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            episodes: List[Episode] = []

            if season_id:
                url = f"{self._base_url}/ajax/season/episodes/{season_id}"
                response = self.http_client.request("GET", url)
                response.raise_for_status()

                soup = self.soup(response.text)

                for tag in soup.select(".nav > li"):
                    episode_id = str(cast(Tag, tag.select_one("a"))["id"]).split("-")[1]
                    episode_number = int(
                        str(cast(Tag, tag.select_one("a"))["title"]).split(":")[0][3:]
                    )

                    episodes.append(Episode(episode_id, 1, episode_number))

            else:
                url = f"{self._base_url}/{media_id}"
                response = self.http_client.request("GET", url)
                response.raise_for_status()

                soup = self.soup(response.text)

                episode_id = str(
                    cast(Tag, soup.select_one(".detail_page-watch"))["data-id"]
                )

                episodes.append(Episode(episode_id, 1, 1))

            return episodes

        except Exception as e:
            raise e
