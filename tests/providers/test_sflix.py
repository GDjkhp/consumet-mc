from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers.sflix import Sflix


@pytest.fixture
def sflix():
    client = HTTPClient()
    config: Config = Config()
    provider = Sflix(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def vincenzo_metadata():
    return Metadata("tv/free-vincenzo-hd-67955", "vincenzo", MetadataType.MULTI)


def test_search(sflix: Sflix):
    sflix.options["mode"] = "title"
    metadatas: List[Metadata] = sflix.search("naruto")
    assert metadatas


def test_search_recent_movies(sflix: Sflix):
    metadatas: List[Metadata] = sflix.search("recent-movies")
    assert metadatas


def test_search_trending_movies(sflix: Sflix):
    metadatas: List[Metadata] = sflix.search("trending-movies")
    assert metadatas


def test_search_trending_tv_show(sflix: Sflix):
    metadatas: List[Metadata] = sflix.search("trending-tv-shows")
    assert metadatas


def test_scrape_episodes(sflix: Sflix, vincenzo_metadata: Metadata):
    episodes: Dict = sflix.scrape_episodes(vincenzo_metadata)
    assert episodes.get(1) == 20


def test_scrape_media_with_upcloud_server_selected(sflix: Sflix, vincenzo_metadata):
    sflix.options["server"] = "upcloud"
    media: Optional[Media] = sflix.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
    assert media


def test_scrape_media_with_akcloud_server_selected(sflix: Sflix, vincenzo_metadata):
    sflix.options["server"] = "akcloud"
    media: Optional[Media] = sflix.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
    assert media


# def test_scrape_media_with_megacloud_server_selected(sflix: Sflix, vincenzo_metadata):
#     sflix.options["server"] = "megacloud"
#     media: Optional[Media] = sflix.scrape(vincenzo_metadata, EpisodeSelector(1, 1))
#     assert media
