from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class PagedResult:
    results: List[Any] = field(default_factory=list)
    current_page: int = field(default=0)
    has_next_page: bool = field(default=False)
