from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ScrapedData:
    """
    Standardized data returned by any scraper provider.
    """
    # Metadata
    title: Optional[str] = None
    description: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    genre: Optional[str] = None
    players: Optional[str] = None
    release_date: Optional[str] = None
    rating: Optional[str] = None
    
    # Artwork URLs
    boxart_2d: Optional[str] = None
    boxart_3d: Optional[str] = None
    background: Optional[str] = None
    logo: Optional[str] = None
    manual: Optional[str] = None
    screenshot: Optional[str] = None
    
    # Source Info
    source_name: str = "Unknown"
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary, keeping only non-None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def merge(self, other: 'ScrapedData'):
        """
        Merge another ScrapedData into this one, keeping existing values if present.
        """
        if not other: return
        
        for key, value in other.__dict__.items():
            if key == "extra_data":
                self.extra_data.update(value)
                continue
            
            # If we don't have a value for this key, take it from 'other'
            if getattr(self, key) is None:
                setattr(self, key, value)
