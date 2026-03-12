from abc import ABC, abstractmethod
import aiohttp
from typing import Optional, Dict, Any

class BaseScraper(ABC):
    """
    Base class for all scrapers (Artwork and Metadata).
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Fetches data for a given query.
        Returns a dictionary or None if not found.
        """
        pass
