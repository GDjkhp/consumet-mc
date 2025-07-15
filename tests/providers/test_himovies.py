from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers.himovies import HiMovies


@pytest.fixture
def himovies():
    client = HTTPClient()
    config: Config = Config()
    provider = HiMovies(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def vincenzo_metadata():
    return Metadata("tv/vincenzo-67955", "vincenzo", MetadataType.MULTI)


def test_search(himovies: HiMovies):
    himovies.options["mode"] = "title"
    metadatas: List[Metadata] = himovies.search("naruto")
    assert metadatas


def test_search_recent_movies(himovies: HiMovies):
    metadatas: List[Metadata] = himovies.search("recent-movies")
    assert metadatas


def test_search_trending_movies(himovies: HiMovies):
    metadatas: List[Metadata] = himovies.search("trending-movies")
    assert metadatas


def test_search_trending_tv_show(himovies: HiMovies):
    metadatas: List[Metadata] = himovies.search("trending-tv-shows")
    assert metadatas


def test_scrape_episodes(himovies: HiMovies, vincenzo_metadata: Metadata):
    episodes: Dict = himovies.scrape_episodes(vincenzo_metadata)
    assert episodes.items()


def test_scrape_media_with_upcloud_server_selected(
    himovies: HiMovies, vincenzo_metadata
):
    himovies.options["server"] = "upcloud"
    media: Optional[Media] = himovies.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
    assert media


def test_scrape_media_with_akcloud_server_selected(
    himovies: HiMovies, vincenzo_metadata
):
    himovies.options["server"] = "akcloud"
    media: Optional[Media] = himovies.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
    assert media


# def test_scrape_media_with_megacloud_server_selected(
#     himovies: HiMovies, vincenzo_metadata
# ):
#     himovies.options["server"] = "megacloud"
#     media: Optional[Media] = himovies.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
#     assert media
