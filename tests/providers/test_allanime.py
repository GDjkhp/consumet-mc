from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers.allanime import AllAnime


@pytest.fixture
def allanime():
    client = HTTPClient()
    config: Config = Config()
    provider = AllAnime(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def naruto_metadata():
    return Metadata("cstcbG4EquLyDnAwN", "Naruto", MetadataType.MULTI)


@pytest.fixture
def solo_leveling_metadata():
    return Metadata("B6AMhLy6EQHDgYgBF", "Solo Leveling", MetadataType.MULTI)


def test_search(allanime: AllAnime):
    allanime.options["mode"] = "title"
    metadatas: List[Metadata] = allanime.search("naruto")
    assert metadatas


def test_scrape_episodes(allanime: AllAnime, naruto_metadata: Metadata):
    episodes: Dict = allanime.scrape_episodes(naruto_metadata)
    assert episodes.items()


def test_scrape_media_with_yt_mp4_server_selected(allanime: AllAnime, naruto_metadata):
    allanime.options["server"] = "yt-mp4"
    media: Optional[Media] = allanime.scrape(naruto_metadata, EpisodeSelector(1, 1))
    assert media


def test_scrape_media_with_mp4_server_selected(
    allanime: AllAnime, solo_leveling_metadata
):
    allanime.options["server"] = "mp4"
    media: Optional[Media] = allanime.scrape(
        solo_leveling_metadata, EpisodeSelector(1, 1)
    )
    assert media


def test_scrape_media_with_fm_hls_server_selected(
    allanime: AllAnime, solo_leveling_metadata
):
    allanime.options["server"] = "fm-hls"
    media: Optional[Media] = allanime.scrape(
        solo_leveling_metadata, EpisodeSelector(1, 1)
    )
    assert media
