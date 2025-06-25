from typing import Dict, List, Optional
from mov_cli.config import Config
from mov_cli.media import Media, Metadata, MetadataType
from mov_cli.http_client import HTTPClient
from mov_cli.utils import EpisodeSelector
import pytest
from consumet_mc.providers.turkish import Turkish


@pytest.fixture
def turkish():
    client = HTTPClient()
    config: Config = Config()
    provider = Turkish(config, client)
    provider.options["mode"] = "category"
    return provider


@pytest.fixture
def sen_cal_kapimi_metadata():
    return Metadata("sen-cal-kapimi", "sen-cal-kapimi", MetadataType.MULTI)


def test_search(turkish: Turkish):
    turkish.options["mode"] = "title"
    metadatas: List[Metadata] = turkish.search("sen")
    assert metadatas


def test_search_recent_movies(turkish: Turkish):
    metadatas: List[Metadata] = turkish.search("series-list")
    assert metadatas


def test_scrape_episodes(turkish: Turkish, sen_cal_kapimi_metadata: Metadata):
    episodes: Dict = turkish.scrape_episodes(sen_cal_kapimi_metadata)
    assert episodes.items()


def test_scrape_media(turkish: Turkish, sen_cal_kapimi_metadata):
    media: Optional[Media] = turkish.scrape(
        sen_cal_kapimi_metadata, EpisodeSelector(1, 1)
    )
    assert media
