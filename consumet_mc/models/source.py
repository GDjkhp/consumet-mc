from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .subtitle import Subtitle
from .video import Video


@dataclass
class Source:
    videos: List[Video]
    subtitles: Optional[List[Subtitle]] = field(default=None)
    headers: Dict[str, str] = field(default_factory=dict)
