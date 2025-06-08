from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Any, Dict


@dataclass
class VideoServer:
    name: str
    embed: str
    alternative_name: Optional[str] = field(default=None)
    extra_data: Dict[str, Any] = field(default_factory=dict)
