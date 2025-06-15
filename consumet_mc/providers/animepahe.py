from __future__ import annotations

from typing import TYPE_CHECKING, cast

from consumet_mc.extractors.kwik import Kwik
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

__all__ = ("AnimePahe",)


class AnimePahe(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)
        self.base_url: str = "https://animepahe.ru"

    def search(self, query: str, limit: Optional[int] = None) -> List[Metadata]:
        limit = 1 if limit is None else limit
        page = cast(int, self.options.get("page", 1))
        search_mode = cast(str, self.options.get("mode", "title"))

        if search_mode == "title":
            return self._search(query, page).results
        elif search_mode == "category":
            if query.strip().lower() == "latest-releases":
                return self._scrape_latest_releases(page).results
            raise Exception("Unsupported query")
        else:
            raise Exception("Unsupported mode")

    def _search(self, query: str, page: int) -> PagedResult:
        try:
            url = f"{self.base_url}/api?m=search&q={query}&{str(page)}"
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

    def _scrape_latest_releases(self, page: int):
        try:
            url = f"{self.base_url}/api?m=airing&page={str(page)}"
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

    def scrape(
        self, metadata: Metadata, episode: EpisodeSelector
    ) -> Optional[Multi | Single]:
        sub_or_dub = self.options.get("sub_or_dub", "any")
        server_name = None

        episodes = self._scrape_episodes(metadata.id)
        episodes.reverse()
        selected_episode = episodes[-episode.episode]

        video_servers = self._scrape_video_servers(selected_episode.id, metadata.id)

        if not video_servers:
            return None

        dub_video_servers: List[VideoServer] = list(
            filter(
                lambda x: x.extra_data.get("sub_or_dub") == "dub",
                video_servers,
            )
        )

        sub_video_servers: List[VideoServer] = list(
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

        if selected_video_server.name == StreamingServer.KWIK:
            video_extractor = Kwik(self.http_client)
            videos = video_extractor.extract(
                selected_video_server.url, referer=self.base_url
            )
            if not videos:
                return None
            video = videos[0]
            subtitles = None
            if metadata.type == MetadataType.MULTI:
                return Multi(video.url, metadata.title, episode, subtitles=subtitles)
            else:
                return Single(video.url, metadata.title, subtitles=subtitles)
        return None

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        try:
            url = f"{self.base_url}/play/{media_id}/{episode_id}"
            response = self.http_client.request(
                "GET", url, headers=self._headers(episode_id)
            )
            response.raise_for_status()

            soup = self.soup(response.text)

            server_tags = soup.select("div#resolutionMenu > button")
            servers = []

            for server_tag in server_tags:
                server_url = cast(str, server_tag["data-src"])
                server_audio = cast(str, server_tag["data-audio"])
                server_quality = server_tag.text

                server_name = StreamingServer.KWIK
                servers.append(
                    VideoServer(
                        server_name,
                        server_url,
                        extra_data={
                            "sub_or_dub": "dub" if "eng" in server_audio else "sub",
                            "quality": server_quality,
                        },
                    )
                )

            return servers

        except Exception as e:
            raise e

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        try:
            current_page = 1
            episodes: List[Episode] = []
            while True:
                url = f"{self.base_url}/api?m=release&id={media_id}&sort=episode_asc&page={str(current_page)}"
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

    def scrape_episodes(self, metadata: Metadata) -> ScrapeEpisodesT:
        episodes = self._scrape_episodes(metadata.id)

        return {1: len(episodes)}

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
            "Referer": f"{self.base_url}/anime/{id}" if id else self.base_url,
        }
