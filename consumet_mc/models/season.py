from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Season:
    id: str
    season_number: int
    title: Optional[str] = field(default=None)
    image_url: Optional[str] = field(default=None)
