from typing import List, Optional
from core.models import Listing
from sources.base import BaseSource

class SbazarSource(BaseSource):
    name = "Sbazar"

    def search(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        postal_code: Optional[str] = None,
        radius_km: Optional[int] = None
    ) -> List[Listing]:
        url = "https://www.sbazar.cz/api/v1/items/search"
        params = {
            "phrase": query,
            "limit": 40
        }
        if min_price is not None and min_price > 0:
            params["price_from"] = int(min_price)
        if max_price is not None and max_price > 0:
            params["price_to"] = int(max_price)

        resp = self.fetcher.get(url, params=params)
        if not resp or resp.status_code != 200:
            return []

        try:
            data = resp.json()
        except Exception:
            return []

        items = []
        for raw in data.get("results", []):
            title = raw.get("name", "").strip()
            if not title:
                continue

            price_val = raw.get("price")
            is_agreement = raw.get("price_by_agreement", False)
            price = None if (is_agreement or price_val is None or price_val == 0) else float(price_val)

            # Client-side price filter
            if min_price is not None and price is not None and price < min_price:
                continue
            if max_price is not None and price is not None and price > max_price:
                continue

            seo_name = raw.get("seo_name") or f"{raw.get('id')}"
            item_url = f"https://www.sbazar.cz/inzerat/{seo_name}"

            # Locality: municipality / district
            loc_data = raw.get("locality") or {}
            muni = loc_data.get("municipality", "")
            dist = loc_data.get("district", "")
            zip_code = loc_data.get("zip", "")
            loc_parts = [p for p in [muni, dist, zip_code] if p]
            location_str = ", ".join(loc_parts)

            # Thumbnail image
            images = raw.get("images", [])
            img_url = images[0].get("url") if images else None

            items.append(Listing(
                title=title,
                price=price,
                url=item_url,
                source=self.name,
                location=location_str,
                image_url=img_url
            ))

        return items
