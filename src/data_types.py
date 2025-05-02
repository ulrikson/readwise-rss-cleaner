from typing import NamedTuple, Dict, List


class SaveAction(NamedTuple):
    """Data transfer object for saving a document to a specific location."""

    doc_id: str
    location: str


class FilterConfig(NamedTuple):
    """Data transfer object for filter configuration and state."""

    standard_filters: Dict[str, List[str]]
    ai_exclude_topics: List[str]
    has_standard_filters: bool
    has_ai_filters: bool

    @property
    def is_valid(self) -> bool:
        """Check if any filters are active."""
        return self.has_standard_filters or self.has_ai_filters
