from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.megacloud.megacloud import Megacloud
from consumet_mc.extractors.video_extractor import StreamingServer
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.season import Season

from ..models import VideoServer
from .provider import Provider

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScrapeEpisodesT, ScraperOptionsT
    from mov_cli.utils import EpisodeSelector

from mov_cli import Metadata, MetadataType, Multi, Single

__all__ = ("Flixhq",)


class Flixhq(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        self.base_url: str = "https://flixhq.to"

        super().__init__(config, http_client, options)

    def search(self, query: str, limit: Optional[int] = None) -> List[Metadata]:
        limit = 1 if limit is None else limit
        page = cast(int, self.options.get("page", 1))
        search_mode = cast(str, self.options.get("mode", "title"))

        if search_mode == "title":
            return self._search(query, page).results
        elif search_mode == "category":
            if query.strip().lower() == "recent-movies":
                return self._scrape_recent_movies().results
            elif query.strip().lower() == "trending-movies":
                return self._scrape_trending_movies().results
            elif query.strip().lower() == "trending-tv-shows":
                return self._scrape_trending_tv_shows().results
            raise Exception("Unsupported query")
        else:
            raise Exception("Unsupported mode")

    def _search(self, query: str, page: int) -> PagedResult:
        url = f"{self.base_url}/search/{query}?page={page}"
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

    def _scrape_recent_movies(self):
        url = f"{self.base_url}/home"
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
        url = f"{self.base_url}/home"
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
        url = f"{self.base_url}/home"
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

    def scrape(
        self, metadata: Metadata, episode: EpisodeSelector
    ) -> Optional[Multi | Single]:
        server_name = self.options.get("server")
        if metadata.type == MetadataType.MULTI:
            seasons = self._scrape_seasons(metadata.id)
            seasons.reverse()
            season_id = seasons[-episode.season].id
            episodes = self._scrape_episodes(metadata.id, season_id)
            episodes.reverse()
            selected_episode = episodes[-episode.episode]

            video_servers = self._scrape_video_servers(selected_episode.id, metadata.id)
        else:
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
            selected_video_server = video_servers[-1]

        if (
            selected_video_server.name == StreamingServer.UPCLOUD
            or selected_video_server.name == StreamingServer.VIDCLOUD
        ):
            video_extractor = Megacloud(self.http_client)
            videos = video_extractor.extract(
                selected_video_server.url, referer=self.base_url
            )
            if not videos:
                return None
            video = videos[0]
            subtitles = None
            if video.subtitles:
                subtitles = list(map(lambda x: x.url, video.subtitles))
            if metadata.type == MetadataType.MULTI:
                return Multi(
                    video.url,
                    metadata.title,
                    episode,
                    subtitles=subtitles,
                    referrer=self.base_url,
                )
            else:
                return Single(video.url, metadata.title, subtitles=subtitles)
        return None

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            if media_id is None:
                return []

            if "movie" not in media_id:
                url = f"{self.base_url}/ajax/v2/episode/servers/{episode_id}"
            else:
                url = f"{self.base_url}/ajax/movie/episodes/{episode_id}"

            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.text)

            server_tags = soup.select(".nav > li")
            servers = []

            for server_tag in server_tags:
                if "movie" not in media_id:
                    data_id = str(cast(Tag, server_tag.select_one("a"))["data-id"])
                    server_name = (
                        str(cast(Tag, server_tag.select_one("a"))["title"])[6:]
                        .strip()
                        .lower()
                    )
                else:
                    data_id = str(cast(Tag, server_tag.select_one("a"))["data-linkid"])
                    server_name = (
                        str(cast(Tag, server_tag.select_one("a"))["title"])
                        .strip()
                        .lower()
                    )

                if server_name == StreamingServer.VIDCLOUD:
                    server_url = self._scrape_video_server_data(data_id)
                    servers.append(
                        VideoServer(
                            server_name,
                            server_url,
                        )
                    )
                elif server_name == StreamingServer.UPCLOUD:
                    server_url = self._scrape_video_server_data(data_id)
                    servers.append(
                        VideoServer(
                            server_name,
                            server_url,
                        )
                    )

            return servers

        except Exception as e:
            raise e

    def _scrape_video_server_data(self, server_data_id: str):
        try:
            url = f"{self.base_url}/ajax/episode/sources/{server_data_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            data = response.json()
            return data["link"]

        except Exception as e:
            raise e

    def _scrape_seasons(self, media_id) -> List[Season]:
        try:
            url = f"{self.base_url}/ajax/v2/tv/seasons/{media_id.split('-')[-1]}"
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
                url = f"{self.base_url}/ajax/v2/season/episodes/{season_id}"
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
                url = f"{self.base_url}/{media_id}"
                response = self.http_client.request("GET", url)
                response.raise_for_status()

                soup = self.soup(response.text)

                episode_id = str(cast(Tag, soup.select_one(".watch_block"))["data-id"])

                episodes.append(Episode(episode_id, 1, 1))

            return episodes

        except Exception as e:
            raise e

    def scrape_episodes(self, metadata: Metadata) -> ScrapeEpisodesT:
        if metadata.type == MetadataType.MULTI:
            scrape_episodes = {}
            seasons = self._scrape_seasons(metadata.id)
            for season in seasons:
                episodes = self._scrape_episodes(metadata.id, season.id)
                scrape_episodes[season.season_number] = len(episodes)

            return scrape_episodes

        else:
            return {None: 1}
