from abc import ABC, abstractmethod
import aiohttp
from typing import Optional
from .models import ScrapedData

class BaseScraper(ABC):
    """
    Base class for all scrapers (Artwork and Metadata).
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[ScrapedData]:
        """
        Fetches data for a given query.
        Returns a ScrapedData object or None if not found.
        """
        pass
