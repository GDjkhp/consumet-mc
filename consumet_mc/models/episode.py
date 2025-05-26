from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Episode:
    id: str
    season_number: int
    episode_number: int
    title: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    duration: Optional[int] = field(default=None)
    image_url: Optional[str] = field(default=None)
