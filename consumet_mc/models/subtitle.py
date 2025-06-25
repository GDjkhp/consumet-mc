from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Subtitle:
    url: str
    lang: Optional[str] = field(default=None)
