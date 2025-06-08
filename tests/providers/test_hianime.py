from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers import HiAnime


@pytest.fixture
def hianime():
    client = HTTPClient()
    config: Config = Config()
    provider = HiAnime(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def naruto_metadata():
    return Metadata("naruto-677", "Naruto", MetadataType.MULTI)


def test_search(hianime: HiAnime):
    hianime.options["mode"] = "title"
    metadatas: List[Metadata] = hianime.search("naruto")
    assert metadatas


def test_search_most_popular(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("most-popular")
    assert metadatas


def test_search_top_airing(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("top-airing")
    assert metadatas


def test_search_most_favorite(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("most-favorite")
    assert metadatas


def test_search_latest_completed(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("latest-completed")
    assert metadatas


def test_search_recently_updated(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("recently-updated")
    assert metadatas


def test_search_recently_added(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("recently-added")
    assert metadatas


def test_search_subbed_anime(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("subbed-anime")
    assert metadatas


def test_search_dubbed_anime(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("dubbed-anime")
    assert metadatas


def test_search_movie(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("movie")
    assert metadatas


def test_search_tv(hianime: HiAnime):
    metadatas: List[Metadata] = hianime.search("tv")
    assert metadatas


def test_scrape_episodes(hianime: HiAnime, naruto_metadata: Metadata):
    episodes: Dict = hianime.scrape_episodes(naruto_metadata)
    assert episodes.items()


def test_scrape_media(hianime: HiAnime, naruto_metadata):
    media: Optional[Media] = hianime.scrape(naruto_metadata, EpisodeSelector(1, 1))
    assert media
