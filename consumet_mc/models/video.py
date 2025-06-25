from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Video:
    url: str
    is_m3u8: Optional[bool] = field(default=False)
    quality: Optional[str] = field(default=None)
