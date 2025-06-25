from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers import AniWorld


@pytest.fixture
def aniworld():
    client = HTTPClient()
    config: Config = Config()
    provider = AniWorld(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def naruto_metadata():
    return Metadata("/anime/stream/naruto", "Naruto", MetadataType.MULTI)


def test_search(aniworld: AniWorld):
    aniworld.options["mode"] = "title"
    metadatas: List[Metadata] = aniworld.search("naruto")
    assert metadatas


def test_search_popular_anime(aniworld: AniWorld):
    metadatas: List[Metadata] = aniworld.search("popular-anime")
    assert metadatas


def test_scrape_episodes(aniworld: AniWorld, naruto_metadata: Metadata):
    episodes: Dict = aniworld.scrape_episodes(naruto_metadata)
    assert episodes.items()


def test_scrape_media_with_filemoon_server_selected(
    aniworld: AniWorld, naruto_metadata
):
    aniworld.options["server"] = "filemoon"
    media: Optional[Media] = aniworld.scrape(naruto_metadata, EpisodeSelector(1, 2))
    assert media


def test_scrape_media_with_veo_server_selected(aniworld: AniWorld, naruto_metadata):
    aniworld.options["server"] = "voe"
    aniworld.options["sub_or_dub"] = "dub"
    media: Optional[Media] = aniworld.scrape(naruto_metadata, EpisodeSelector(1, 2))
    assert media


def test_scrape_media(aniworld: AniWorld, naruto_metadata):
    media: Optional[Media] = aniworld.scrape(naruto_metadata, EpisodeSelector(1, 2))
    assert media
