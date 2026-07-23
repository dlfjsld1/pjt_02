"""PubMed collection feature modules."""

from .collector import collect_papers
from .models import CollectionResult, Paper
from .search_criteria import SearchCriteria, validate_search_criteria

__all__ = [
    "CollectionResult",
    "Paper",
    "SearchCriteria",
    "collect_papers",
    "validate_search_criteria",
]
