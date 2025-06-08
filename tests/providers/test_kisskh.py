from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers import Kisskh


@pytest.fixture
def kisskh():
    client = HTTPClient()
    config: Config = Config()

    provider = Kisskh(config, client)
    provider.options["mode"] = "category"

    return provider


@pytest.fixture
def vincenzo_metadata():
    return Metadata("1219", "Vincenzo (2021)", MetadataType.MULTI)


def test_search(kisskh: Kisskh):
    kisskh.options["mode"] = "title"
    metadatas: List[Metadata] = kisskh.search("vincenzo")
    assert metadatas


def test_search_popular(kisskh: Kisskh):
    metadatas: List[Metadata] = kisskh.search("popular")
    assert metadatas


def test_search_ongoing(kisskh: Kisskh):
    metadatas: List[Metadata] = kisskh.search("ongoing")
    assert metadatas


def test_search_completed(kisskh: Kisskh):
    metadatas: List[Metadata] = kisskh.search("completed")
    assert metadatas


def test_search_movies(kisskh: Kisskh):
    metadatas: List[Metadata] = kisskh.search("movie")
    assert metadatas


def test_search_tv_series(kisskh: Kisskh):
    metadatas: List[Metadata] = kisskh.search("tv")
    assert metadatas


def test_scrape_episodes(kisskh: Kisskh, vincenzo_metadata: Metadata):
    episodes: Dict = kisskh.scrape_episodes(vincenzo_metadata)
    assert episodes.items()


def test_scrape_media(kisskh: Kisskh, vincenzo_metadata: Metadata):
    media: Optional[Media] = kisskh.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
    assert media
