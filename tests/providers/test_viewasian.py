from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers.viewasian import ViewAsian


@pytest.fixture
def viewasian():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    client = HTTPClient(headers=headers)
    config: Config = Config()
    provider = ViewAsian(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def iron_family_metadata():
    return Metadata("/drama/iron-family-2024/", "iron-family", MetadataType.MULTI)


def test_search(viewasian: ViewAsian):
    viewasian.options["mode"] = "title"
    metadatas: List[Metadata] = viewasian.search("ghost")
    assert metadatas


def test_search_most_popular_drama(viewasian: ViewAsian):
    metadatas: List[Metadata] = viewasian.search("most-popular-drama")
    assert metadatas


def test_search_recent_drama(viewasian: ViewAsian):
    metadatas: List[Metadata] = viewasian.search("recent-drama")
    assert metadatas


def test_scrape_episodes(viewasian: ViewAsian, iron_family_metadata: Metadata):
    episodes: Dict = viewasian.scrape_episodes(iron_family_metadata)
    assert episodes.items()


def test_scrape_media(viewasian: ViewAsian, iron_family_metadata):
    media: Optional[Media] = viewasian.scrape(
        iron_family_metadata, EpisodeSelector(20, 1)
    )
    assert media
