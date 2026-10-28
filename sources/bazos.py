import re
from typing import List, Optional
from bs4 import BeautifulSoup
from core.models import Listing
from sources.base import BaseSource

class BazosSource(BaseSource):
    name = "Bazoš"

    def _parse_price(self, text: str) -> Optional[float]:
        if not text:
            return None
        cleaned = re.sub(r"[^\d]", "", text)
        return float(cleaned) if cleaned else None

    def search(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        postal_code: Optional[str] = None,
        radius_km: Optional[int] = None
    ) -> List[Listing]:
        url = "https://www.bazos.cz/search.php"
        params = {
            "hledat": query,
            "rubriky": "bazos",
        }
        if min_price is not None and min_price > 0:
            params["cenaod"] = int(min_price)
        if max_price is not None and max_price > 0:
            params["cenado"] = int(max_price)
        if postal_code:
            clean_zip = re.sub(r"[^\d]", "", postal_code)
            if clean_zip:
                params["hlokalita"] = clean_zip
                if radius_km:
                    params["humkreis"] = int(radius_km)

        resp = self.fetcher.get(url, params=params)
        if not resp or resp.status_code != 200:
            return []

        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []

        for inzerat in soup.find_all("div", class_="inzeraty"):
            title_node = inzerat.find("h2", class_="nadpis")
            if not title_node or not title_node.find("a"):
                continue

            link_tag = title_node.find("a")
            title = link_tag.text.strip()
            item_url = link_tag["href"]
            if item_url.startswith("/"):
                item_url = f"https://www.bazos.cz{item_url}"

            price_node = inzerat.find("div", class_="inzeratycena")
            price = self._parse_price(price_node.text) if price_node else None

            # Location: e.g. "Praha 10<br/>101 00"
            lok_node = inzerat.find("div", class_="inzeratylok")
            location_str = ""
            if lok_node:
                parts = [p.strip() for p in lok_node.stripped_strings]
                location_str = " ".join(parts)

            # Image thumbnail if available
            img_node = inzerat.find("img", class_="obrazek")
            img_url = img_node.get("src") if img_node else None

            # Client-side price check
            if min_price is not None and price is not None and price < min_price:
                continue
            if max_price is not None and price is not None and price > max_price:
                continue

            items.append(Listing(
                title=title,
                price=price,
                url=item_url,
                source=self.name,
                location=location_str,
                image_url=img_url
            ))

        return items
