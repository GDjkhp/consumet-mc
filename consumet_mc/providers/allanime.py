from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from consumet_mc.extractors.builtin import Builtin
from consumet_mc.extractors.filemoon import Filemoon
from consumet_mc.extractors.mp4upload import Mp4Upload
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.episode import Episode
from consumet_mc.models.paged_result import PagedResult
from consumet_mc.models.video_server import VideoServer

from .provider import Provider

if TYPE_CHECKING:
    from typing import List, Optional

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScrapeEpisodesT, ScraperOptionsT

from mov_cli import Metadata, MetadataType
from consumet_mc.utils.utils import USER_AGENT

__all__ = ("AllAnime",)


class AllAnime(Provider):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: ScraperOptionsT | None = None,
    ) -> None:
        super().__init__(config, http_client, options)
        self._images_base_url = "https://wp.youtube-anime.com/aln.youtube-anime.com"

    @property
    def _base_url(self) -> str:
        return "https://api.allanime.day"

    def _search_title(self, query: str, page: int) -> PagedResult:
        SEARCH_GQL = """
        query (
        $search: SearchInput
        $limit: Int
        $page: Int
        $translationType: VaildTranslationTypeEnumType
        $countryOrigin: VaildCountryOriginEnumType
        ) {
        shows(
            search: $search
            limit: $limit
            page: $page
            translationType: $translationType
            countryOrigin: $countryOrigin
        ) {
            pageInfo {
            total
            }
            edges {
            _id
            name
            thumbnail
            availableEpisodes
            type
            }
        }
        }
        """
        try:
            sub_or_dub = cast(str, self.options.get("sub_or_dub", "sub"))
            url = f"{self._base_url}/api"
            variables = {
                "search": {
                    "allowAdult": False,
                    "allowUnknown": False,
                    "query": query,
                },
                "limit": 26,
                "page": page,
                "translationType": sub_or_dub,
                "countryOrigin": "ALL",
            }
            json_variable_str = json.dumps(variables)
            params = {"variables": json_variable_str, "query": SEARCH_GQL}
            headers = {"User-Agent": USER_AGENT, "Referer": "https://allmanga.to"}
            response = self.http_client.request(
                "GET", url, headers=headers, params=params
            )
            response.raise_for_status()

            data = response.json()
            paged_result = PagedResult()
            for item in data["data"]["shows"]["edges"]:
                if not item["thumbnail"].startswith("https"):
                    item["thumbnail"] = (
                        f"{self._images_base_url}/{item['thumbnail']}?w=250"
                    )

                paged_result.results.append(
                    Metadata(
                        item["_id"],
                        item["name"],
                        MetadataType.SINGLE
                        if item["type"] == "Movie"
                        else MetadataType.MULTI,
                        item["thumbnail"],
                    )
                )

            return paged_result
        except Exception as e:
            raise e

    def _scrape_video_servers(
        self, episode_id: str, media_id: Optional[str] = None
    ) -> list[VideoServer]:
        EPISODES_GQL = """
        query (
        $showId: String!
        $translationType: VaildTranslationTypeEnumType!
        $episodeString: String!
        ) {
        episode(
            showId: $showId
            translationType: $translationType
            episodeString: $episodeString
        ) {
            episodeString
            sourceUrls
            notes
        }
        }
        """

        try:
            sub_or_dub = cast(str, self.options.get("sub_or_dub", "sub"))
            url = f"{self._base_url}/api"
            variables = {
                "showId": media_id,
                "translationType": sub_or_dub,
                "episodeString": episode_id,
            }
            json_variable_str = json.dumps(variables)
            params = {"variables": json_variable_str, "query": EPISODES_GQL}
            headers = {"User-Agent": USER_AGENT, "Referer": "https://allmanga.to"}
            response = self.http_client.request(
                "GET", url, headers=headers, params=params
            )
            response.raise_for_status()

            data = response.json()
            servers = []

            for item in data["data"]["episode"]["sourceUrls"]:
                server_url = item.get("sourceUrl")
                if not server_url:
                    continue

                if str(server_url).startswith("--"):
                    server_url = bytes(
                        [segment ^ 56 for segment in bytearray.fromhex(server_url[2:])]
                    ).decode("utf-8")

                servers.append(
                    VideoServer(
                        item["sourceName"].lower(),
                        server_url,
                        extra_data={"referer": self._base_url},
                    )
                )
            return servers

        except Exception as e:
            raise e

    def _get_video_extractor(self, server: VideoServer) -> Optional[VideoExtractor]:
        if server.name == "yt-mp4":  # Builtin
            return Builtin(self.http_client, server)
        elif server.name == "mp4":  # MP4UPLOAD
            return Mp4Upload(self.http_client, server)
        elif server.name == "fm-hls":  # FILEMOON
            return Filemoon(self.http_client, server)
        elif server.name == "vid-mp4":  # Unknown
            return None
        elif server.name == "ss-hls":  # STREAMSB
            return None

    def _scrape_episodes(
        self, media_id: str, season_id: Optional[str] = None
    ) -> List[Episode]:
        SHOW_GQL = """
        query ($showId: String!) {
        show(_id: $showId) {
        _id
        name
        availableEpisodesDetail
        }
        }
        """
        try:
            sub_or_dub = cast(str, self.options.get("sub_or_dub", "sub"))
            url = f"{self._base_url}/api"
            variables = {
                "showId": media_id,
            }
            json_variable_str = json.dumps(variables)
            params = {"variables": json_variable_str, "query": SHOW_GQL}
            headers = {"User-Agent": USER_AGENT, "Referer": "https://allmanga.to"}
            response = self.http_client.request(
                "GET", url, headers=headers, params=params
            )
            response.raise_for_status()

            data = response.json()

            episodes: List[Episode] = []
            episode_strs = data["data"]["show"]["availableEpisodesDetail"][sub_or_dub]
            episode_strs.reverse()

            for i in range(len(episode_strs)):
                episodes.append(Episode(episode_strs[i], 1, i + 1))

            return episodes

        except Exception as e:
            raise e
