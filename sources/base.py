from abc import ABC, abstractmethod
from typing import List, Optional
from core.models import Listing
from core.fetcher import SafeFetcher

class BaseSource(ABC):
    """Abstract interface for safe marketplace adapters."""

    def __init__(self, fetcher: SafeFetcher):
        self.fetcher = fetcher

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the source platform."""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        postal_code: Optional[str] = None,
        radius_km: Optional[int] = None
    ) -> List[Listing]:
        """Execute a polite, safe search query on the marketplace."""
        pass
