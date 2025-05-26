from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class PagedResult:
    results: List[Any] = field(default_factory=list)
    current_page: int = field(default=1)
    total_pages: int = field(default=1)
    has_next_page: bool = field(default=False)
