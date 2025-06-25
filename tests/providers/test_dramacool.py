from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers import DramaCool


@pytest.fixture
def dramacool():
    client = HTTPClient()
    config: Config = Config()
    provider = DramaCool(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def iron_family_metadata():
    return Metadata(
        "/episodes/iron-family-2024-episode-1/", "iron family 2024", MetadataType.MULTI
    )


def test_search(dramacool: DramaCool):
    dramacool.options["mode"] = "title"
    metadatas: List[Metadata] = dramacool.search("iron")
    assert metadatas


def test_search_recent_drama(dramacool: DramaCool):
    metadatas: List[Metadata] = dramacool.search("recent-drama")
    assert metadatas


def test_search_recent_movies(dramacool: DramaCool):
    metadatas: List[Metadata] = dramacool.search("recent-movies")
    assert metadatas


def test_scrape_episodes(dramacool: DramaCool, iron_family_metadata: Metadata):
    episodes: Dict = dramacool.scrape_episodes(iron_family_metadata)
    assert episodes.items()


def test_scrape_media_with_streamwish(dramacool: DramaCool, iron_family_metadata):
    dramacool.options["server"] = "streamwish"
    media: Optional[Media] = dramacool.scrape(
        iron_family_metadata, EpisodeSelector(1, 1)
    )
    assert media
