import re
import json
from typing import List, Optional
from core.models import Listing
from sources.base import BaseSource

class AukroSource(BaseSource):
    name = "Aukro"

    def search(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        postal_code: Optional[str] = None,
        radius_km: Optional[int] = None
    ) -> List[Listing]:
        url = "https://aukro.cz/vysledky-vyhledavani"
        params = {"text": query}

        resp = self.fetcher.get(url, params=params)
        if not resp or resp.status_code != 200:
            return []

        scripts = re.findall(r'<script[^>]*>(.*?)</script>', resp.text, re.DOTALL)
        items = []

        # 1. First attempt: aukCache (primary SSR cache containing up to 60 structured search items)
        for s in scripts:
            if "aukCache" in s:
                try:
                    cache = json.loads(s).get("aukCache", {})
                    for k, v in cache.items():
                        if "searchItemsCommon" in k and isinstance(v, dict):
                            content = v.get("b", {}).get("content", [])
                            for it in content:
                                title = it.get("itemName")
                                if not title:
                                    continue
                                
                                price_val = (it.get("price") or {}).get("amount")
                                try:
                                    price = float(price_val) if price_val is not None else None
                                except (ValueError, TypeError):
                                    price = None

                                # Client-side price filter
                                if min_price is not None and price is not None and price < min_price:
                                    continue
                                if max_price is not None and price is not None and price > max_price:
                                    continue

                                item_id = it.get("itemId")
                                seo_url = it.get("seoUrl")
                                item_url = f"https://aukro.cz/{seo_url}-{item_id}" if (seo_url and item_id) else "https://aukro.cz"

                                loc = it.get("location") or ""
                                post = it.get("postcode") or ""
                                loc_str = f"{loc} {post}".strip() or "ČR (Doručení / Osobní)"
                                img_url = it.get("titleImageUrl")

                                items.append(Listing(
                                    title=title,
                                    price=price,
                                    url=item_url,
                                    source=self.name,
                                    location=loc_str,
                                    image_url=img_url
                                ))
                except Exception:
                    pass

        # 2. Fallback attempt: Schema.org ItemList JSON-LD
        if not items:
            for s in scripts:
                if 'application/ld+json' in s or '"@type":"ItemList"' in s:
                    try:
                        data = json.loads(s)
                        main_entity = data.get("mainEntity", {})
                        if main_entity.get("@type") == "ItemList":
                            for raw in main_entity.get("itemListElement", []):
                                title = raw.get("name", "").strip()
                                item_url = raw.get("url", "")
                                if not title or not item_url:
                                    continue

                                offers = raw.get("offers", {})
                                price_val = offers.get("price")
                                try:
                                    price = float(price_val) if price_val is not None else None
                                except (ValueError, TypeError):
                                    price = None

                                if min_price is not None and price is not None and price < min_price:
                                    continue
                                if max_price is not None and price is not None and price > max_price:
                                    continue

                                items.append(Listing(
                                    title=title,
                                    price=price,
                                    url=item_url,
                                    source=self.name,
                                    location="ČR (Doručení / Osobní)",
                                    image_url=raw.get("image")
                                ))
                    except Exception:
                        pass

        return items
