from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bs4.element import Tag

from consumet_mc.extractors.megacloud.megacloud import Megacloud
from consumet_mc.extractors.video_extractor import StreamingServer
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

__all__ = ("HiAnime",)


class HiAnime(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        self.base_url: str = "https://hianime.to"

        super().__init__(config, http_client, options)

    def search(self, query: str, limit: Optional[int] = None) -> List[Metadata]:
        limit = 1 if limit is None else limit
        page = cast(int, self.options.get("page", 1))
        search_mode = cast(str, self.options.get("mode", "title"))

        if search_mode == "title":
            return self._search(query, page).results
        elif search_mode == "category":
            if query.strip().lower() == "most-popular":
                return self._scrape_most_popular(page).results
            elif query.strip().lower() == "top-airing":
                return self._scrape_top_airing(page).results
            elif query.strip().lower() == "most-favorite":
                return self._scrape_most_favorite(page).results
            elif query.strip().lower() == "latest-completed":
                return self._scrape_latest_completed(page).results
            elif query.strip().lower() == "recently-updated":
                return self._scrape_recently_updated(page).results
            elif query.strip().lower() == "recently-added":
                return self._scrape_recently_added(page).results
            elif query.strip().lower() == "subbed-anime":
                return self._scrape_subbed_anime(page).results
            elif query.strip().lower() == "dubbed-anime":
                return self._scrape_dubbed_anime(page).results
            elif query.strip().lower() == "movie":
                return self._scrape_movie(page).results
            elif query.strip().lower() == "tv":
                return self._scrape_tv(page).results
            raise Exception("Unsupported query")
        else:
            raise Exception("Unsupported mode")

    def _search(self, query: str, page: int) -> PagedResult:
        url = f"{self.base_url}/search/?keyword={query}&page={page}"
        return self._scrape_card_page(url)

    def _scrape_most_popular(self, page: int):
        url = f"{self.base_url}/most-popular?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_top_airing(self, page: int):
        url = f"{self.base_url}/top-airing?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_most_favorite(self, page: int):
        url = f"{self.base_url}/most-favorite?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_latest_completed(self, page: int):
        url = f"{self.base_url}/completed?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_recently_updated(self, page: int):
        url = f"{self.base_url}/recently-updated?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_recently_added(self, page: int):
        url = f"{self.base_url}/recently-added?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_subbed_anime(self, page: int):
        url = f"{self.base_url}/subbed-anime?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_dubbed_anime(self, page: int):
        url = f"{self.base_url}/dubbed-anime?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_movie(self, page: int):
        url = f"{self.base_url}/movie?page={str(page)}"
        return self._scrape_card_page(url)

    def _scrape_tv(self, page: int):
        url = f"{self.base_url}/tv?page={str(page)}"
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

    def scrape(
        self, metadata: Metadata, episode: EpisodeSelector
    ) -> Optional[Multi | Single]:
        sub_or_dub = self.options.get("sub_or_dub", "any")
        server_name = self.options.get("server")

        episodes = self._scrape_episodes(metadata.id)
        episodes.reverse()
        selected_episode = episodes[-episode.episode]

        video_servers = self._scrape_video_servers(selected_episode.id)

        if not video_servers:
            return None

        dub_video_servers = list(
            filter(
                lambda x: x.extra_data.get("sub_or_dub") == "dub",
                video_servers,
            )
        )

        sub_video_servers = list(
            filter(
                lambda x: x.extra_data.get("sub_or_dub") == "sub",
                video_servers,
            )
        )

        selected_video_server = None

        if sub_or_dub == "dub":
            if not dub_video_servers:
                raise Exception("No dub video server found")

            if server_name:
                for s in dub_video_servers:
                    if s.name == server_name:
                        selected_video_server = s
                        break
                if not selected_video_server:
                    raise Exception(f"No video server found with name {server_name}")
            else:
                selected_video_server = dub_video_servers[-1]

        elif sub_or_dub == "sub":
            if not sub_video_servers:
                raise Exception("No sub video server found")

            if server_name:
                for s in sub_video_servers:
                    if s.name == server_name:
                        selected_video_server = s
                        break
                if not selected_video_server:
                    raise Exception(f"No video server found with name {server_name}")
            else:
                selected_video_server = sub_video_servers[-1]

        elif sub_or_dub == "any":
            if server_name:
                for s in video_servers:
                    if s.name == server_name:
                        selected_video_server = s
                        break
                if not selected_video_server:
                    raise Exception(f"No video server found with name {server_name}")
            else:
                selected_video_server = video_servers[-1]

        else:
            return None

        if StreamingServer.MEGACLOUD in selected_video_server.name:
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
                return Multi(video.url, metadata.title, episode, subtitles=subtitles)
            else:
                return Single(video.url, metadata.title, subtitles=subtitles)
        return None

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            url = f"{self.base_url}/ajax/v2/episode/servers?episodeId={episode_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            soup = self.soup(response.json()["html"])

            server_tags = soup.select(".item.server-item")
            servers = []

            for server_tag in server_tags:
                server_internal_name = str(
                    cast(Tag, server_tag.select_one("a")).text
                ).strip()
                data_id = cast(str, server_tag["data-id"])
                data_type = cast(str, server_tag["data-type"])

                # * megacloud -> HD-1 HD-2 HD-3

                if "HD" in server_internal_name:
                    server_url = self._scrape_video_server_data(data_id)
                    server_number = server_internal_name.split("-")[-1]
                    server_name = f"{StreamingServer.MEGACLOUD}-{server_number}"

                    servers.append(
                        VideoServer(
                            server_name,
                            server_url,
                            extra_data={
                                "sub_or_dub": data_type,
                            },
                        )
                    )

            return servers

        except Exception as e:
            raise e

    def _scrape_video_server_data(self, server_data_id: str):
        try:
            url = f"{self.base_url}/ajax/v2/episode/sources/?id={server_data_id}"
            response = self.http_client.request("GET", url)
            response.raise_for_status()

            data = response.json()
            return data["link"]

        except Exception as e:
            raise e

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            url = f"{self.base_url}/ajax/v2/episode/list/{media_id.split('-')[-1]}"
            headers = {
                "X-Requested-with": "XMLHttpRequest",
                "Referer": f"{self.base_url}/watch/{media_id}",
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

    def scrape_episodes(self, metadata: Metadata) -> ScrapeEpisodesT:
        episodes = self._scrape_episodes(metadata.id)

        return {1: len(episodes)}
