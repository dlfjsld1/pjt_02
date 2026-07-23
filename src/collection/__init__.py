"""PubMed collection feature modules."""

from .collector import collectPapers
from .models import CollectionResult, Paper
from .searchCriteria import SearchCriteria, validateSearchCriteria

__all__ = [
    "CollectionResult",
    "Paper",
    "SearchCriteria",
    "collectPapers",
    "validateSearchCriteria",
]
