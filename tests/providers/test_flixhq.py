from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers.flixhq import Flixhq


@pytest.fixture
def flixhq():
    client = HTTPClient()
    config: Config = Config()
    provider = Flixhq(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def vincenzo_metadata():
    return Metadata("tv/watch-vincenzo-67955", "vincenzo", MetadataType.MULTI)


def test_search(flixhq: Flixhq):
    flixhq.options["mode"] = "title"
    metadatas: List[Metadata] = flixhq.search("naruto")
    assert metadatas


def test_search_recent_movies(flixhq: Flixhq):
    metadatas: List[Metadata] = flixhq.search("recent-movies")
    assert metadatas


def test_search_trending_movies(flixhq: Flixhq):
    metadatas: List[Metadata] = flixhq.search("trending-movies")
    assert metadatas


def test_search_trending_tv_show(flixhq: Flixhq):
    metadatas: List[Metadata] = flixhq.search("trending-tv-shows")
    assert metadatas


def test_scrape_episodes(flixhq: Flixhq, vincenzo_metadata: Metadata):
    episodes: Dict = flixhq.scrape_episodes(vincenzo_metadata)
    assert episodes.items()


def test_scrape_media(flixhq: Flixhq, vincenzo_metadata):
    media: Optional[Media] = flixhq.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
    assert media
