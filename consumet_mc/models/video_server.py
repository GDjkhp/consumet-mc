from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict


@dataclass
class VideoServer:
    name: str
    embed: str
    extraData: Dict[str, Any] = field(default_factory=dict)
