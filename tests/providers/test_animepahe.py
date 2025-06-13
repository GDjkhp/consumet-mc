from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers import AnimePahe


@pytest.fixture
def animepahe():
    client = HTTPClient()
    config: Config = Config()
    provider = AnimePahe(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def naruto_metadata():
    return Metadata(
        "78e38106-d9f3-a8b5-7974-9702f603dc96", "Naruto", MetadataType.MULTI
    )


def test_search(animepahe: AnimePahe):
    animepahe.options["mode"] = "title"
    metadatas: List[Metadata] = animepahe.search("naruto")
    assert metadatas


def test_search_latest_releases(animepahe: AnimePahe):
    metadatas: List[Metadata] = animepahe.search("latest-releases")
    assert metadatas


def test_scrape_episodes(animepahe: AnimePahe, naruto_metadata: Metadata):
    episodes: Dict = animepahe.scrape_episodes(naruto_metadata)
    assert episodes.items()


def test_scrape_media(animepahe: AnimePahe, naruto_metadata):
    media: Optional[Media] = animepahe.scrape(naruto_metadata, EpisodeSelector(1, 1))
    assert media
