from dataclasses import dataclass
from typing import Optional

@dataclass
class Listing:
    title: str
    price: Optional[float]
    url: str
    source: str
    location: str = ""
    distance_km: Optional[float] = None
    currency: str = "Kč"
    image_url: Optional[str] = None

    @property
    def price_display(self) -> str:
        if self.price is None or self.price == 0:
            return "Dohodou / Neuvedeno"
        return f"{int(self.price):,} {self.currency}".replace(",", " ")
