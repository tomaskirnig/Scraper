import re
from typing import List, Optional
from core.models import Listing
from core.fetcher import SafeFetcher
from core.geo import GeoResolver, haversine_km
from sources.bazos import BazosSource
from sources.sbazar import SbazarSource
from sources.aukro import AukroSource

class SafeAggregator:
    def __init__(self, fetcher: Optional[SafeFetcher] = None):
        self.fetcher = fetcher or SafeFetcher()
        self.geo = GeoResolver()
        self.sources = {
            "Bazoš": BazosSource(self.fetcher),
            "Sbazar": SbazarSource(self.fetcher),
            "Aukro": AukroSource(self.fetcher),
        }

    def _extract_postal_code(self, location_str: str) -> Optional[str]:
        match = re.search(r"\b(\d{3})\s*(\d{2})\b", location_str)
        if match:
            return f"{match.group(1)}{match.group(2)}"
        return None

    def search(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        origin_place: Optional[str] = None,
        max_distance_km: Optional[int] = None,
        enabled_sources: Optional[List[str]] = None,
        include_nationwide: bool = True
    ) -> List[Listing]:
        if not query or not query.strip():
            return []

        enabled = enabled_sources or list(self.sources.keys())
        all_results: List[Listing] = []

        origin_zip = self._extract_postal_code(origin_place) if origin_place else None

        for name in enabled:
            source = self.sources.get(name)
            if not source:
                continue

            try:
                results = source.search(
                    query=query.strip(),
                    min_price=min_price,
                    max_price=max_price,
                    postal_code=origin_zip,
                    radius_km=max_distance_km
                )
                all_results.extend(results)
            except Exception:
                continue

        # If origin location and max distance are given, filter and calculate distance
        if origin_place and max_distance_km is not None and max_distance_km > 0:
            # allow_network=True ONLY for origin, never for batch items
            origin_coords = self.geo.get_coords(origin_place, allow_network=True)
            if origin_coords:
                filtered_results = []
                for item in all_results:
                    # Check if nationwide (e.g. Aukro delivery or general ČR)
                    if "ČR" in item.location or "Doručení" in item.location:
                        if include_nationwide:
                            filtered_results.append(item)
                        continue

                    # Instant offline resolution for item location
                    item_zip = self._extract_postal_code(item.location)
                    item_coords = None

                    if item_zip:
                        item_coords = self.geo.get_coords(item_zip, allow_network=False)
                    if not item_coords and item.location:
                        city_part = item.location.split(",")[0].strip()
                        item_coords = self.geo.get_coords(city_part, allow_network=False)

                    if item_coords:
                        dist = haversine_km(origin_coords[0], origin_coords[1], item_coords[0], item_coords[1])
                        item.distance_km = dist
                        if dist <= max_distance_km:
                            filtered_results.append(item)
                    else:
                        if include_nationwide:
                            filtered_results.append(item)

                all_results = filtered_results

        return all_results
