import math
import json
import os
import time
import requests
from typing import Optional, Tuple

# Pre-seeded common Czech district hubs (lat, lon)
CZECH_DISTRICT_HUBS = {
    "praha": (50.0875, 14.4213),
    "brno": (49.1951, 16.6068),
    "ostrava": (49.8209, 18.2625),
    "plzen": (49.7475, 13.3776),
    "liberec": (50.7671, 15.0562),
    "olomouc": (49.5938, 17.2509),
    "ceske budejovice": (48.9745, 14.4743),
    "hradec kralove": (50.2092, 15.8328),
    "usti nad labem": (50.6607, 14.0323),
    "pardubice": (50.0343, 15.7812),
    "zlin": (49.2227, 17.6667),
    "kladno": (50.1473, 14.1029),
    "most": (50.5030, 13.6362),
    "karvina": (49.8540, 18.5417),
    "opava": (49.9387, 17.9026),
    "frydek-mistek": (49.6853, 18.3492),
    "karlovy vary": (50.2319, 12.8720),
    "teplice": (50.6404, 13.8245),
    "decin": (50.7822, 14.2148),
    "jihlava": (49.3961, 15.5912),
    "prostejov": (49.4719, 17.1128),
    "prerov": (49.4551, 17.4509),
    "ceska lipa": (50.6855, 14.5376),
    "trebic": (49.2149, 15.8817),
    "tabor": (49.4144, 14.6578),
    "znojmo": (48.8555, 16.0488),
    "pribram": (49.6899, 14.0104),
    "cheb": (50.0796, 12.3739),
    "kolin": (50.0281, 15.2006),
    "trutnov": (50.5610, 15.9128),
    "kromeriz": (49.2979, 17.3931),
    "vsetin": (49.3387, 17.9962),
    "sumperk": (49.9653, 16.9706),
    "valasske mezirici": (49.4718, 17.9711),
    "litomerice": (50.5341, 14.1318),
    "nachod": (50.4167, 16.1629),
    "jablonec nad nisou": (50.7243, 15.1711),
    "mlada boleslav": (50.4114, 14.9032),
    "kutna hora": (49.9500, 15.2667),
    "beroun": (49.9644, 14.0722),
    "melnik": (50.3506, 14.4744),
    "benesov": (49.7822, 14.6869),
    "strakonice": (49.2614, 13.9025),
    "pisek": (49.3089, 14.1475),
    "jindrichuv hradec": (49.1442, 15.0031),
    "pelhrimov": (49.4311, 15.2236),
    "breclav": (48.7589, 16.8822),
    "hodonin": (48.8489, 17.1325),
    "uherske hradiste": (49.0697, 17.4597),
    "blansko": (49.3631, 16.6444),
    "vyskov": (49.2778, 16.9989),
    "svitavy": (49.7561, 16.4689),
    "usti nad orlici": (49.9744, 16.3939),
    "chrudim": (49.9511, 15.7956),
    "havlickuv brod": (49.6078, 15.5806),
    "zdar nad sazavou": (49.5628, 15.9392),
    "rychnov nad kneznou": (50.1628, 16.2750),
    "semily": (50.6019, 15.3356),
    "jicin": (50.4372, 15.3517),
    "louny": (50.3569, 13.7967),
    "chomutov": (50.4606, 13.4178),
    "litvinov": (50.5989, 13.6106),
    "sokolov": (50.1814, 12.6406),
    "domazlice": (49.4406, 12.9297),
    "klatovy": (49.3956, 13.2950),
    "rokycany": (49.7428, 13.5939),
    "tachov": (49.7950, 12.6339),
    "jesenik": (50.2294, 17.2047),
    "bruntal": (49.9883, 17.4647),
    "novy jicin": (49.5944, 18.0103),
    "bohumin": (49.9039, 18.3578),
    "havirov": (49.7797, 18.4369),
    "trinec": (49.6778, 18.6706),
}

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "geo_cache.json")


def _strip_accents(text: str) -> str:
    accents = {
        'á': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'ě': 'e', 'í': 'i', 'ň': 'n',
        'ó': 'o', 'ř': 'r', 'š': 's', 'ť': 't', 'ú': 'u', 'ů': 'u', 'ý': 'y', 'ž': 'z'
    }
    t = text.lower()
    for accented, plain in accents.items():
        t = t.replace(accented, plain)
    return t


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two coordinate pairs using Haversine formula."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 1)


def approx_zip_coords(zip_str: str) -> Optional[Tuple[float, float]]:
    """Instant offline fallback from postal code to regional centroid."""
    clean = zip_str.replace(" ", "")
    if len(clean) >= 3 and clean.isdigit():
        p3 = int(clean[:3])
        p2 = int(clean[:2])
        if p2 == 10 or (100 <= p3 <= 199):
            return (50.0875, 14.4213)  # Praha
        if 250 <= p3 <= 299:
            return (50.1000, 14.5000)  # Střední Čechy
        if 301 <= p3 <= 349:
            return (49.7475, 13.3776)  # Plzeňsko
        if 350 <= p3 <= 369:
            return (50.2319, 12.8720)  # Karlovarsko
        if 370 <= p3 <= 399:
            return (48.9745, 14.4743)  # Jižní Čechy
        if 400 <= p3 <= 449:
            return (50.6607, 14.0323)  # Ústecko
        if 460 <= p3 <= 479:
            return (50.7671, 15.0562)  # Liberecko
        if 500 <= p3 <= 529:
            return (50.2092, 15.8328)  # Královéhradecko
        if 530 <= p3 <= 579:
            return (50.0343, 15.7812)  # Pardubicko
        if 580 <= p3 <= 599:
            return (49.3961, 15.5912)  # Vysočina
        if 600 <= p3 <= 679:
            return (49.1951, 16.6068)  # Brno / Jihomoravský
        if 680 <= p3 <= 699:
            return (48.8555, 16.0488)  # Znojmo / Břeclav
        if 700 <= p3 <= 749:
            return (49.8209, 18.2625)  # Moravskoslezsko
        if 750 <= p3 <= 769:
            return (49.2227, 17.6667)  # Zlínsko
        if 770 <= p3 <= 799:
            return (49.5938, 17.2509)  # Olomoucko
    return None


class GeoResolver:
    """Resolves Czech cities or postal codes to GPS coordinates with offline-first caching."""

    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = os.path.abspath(cache_file)
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_coords(self, place_or_zip: str, allow_network: bool = False) -> Optional[Tuple[float, float]]:
        if not place_or_zip:
            return None

        raw_key = place_or_zip.strip()
        normalized_key = _strip_accents(raw_key)

        # 1. Check pre-seeded district hubs
        if normalized_key in CZECH_DISTRICT_HUBS:
            return CZECH_DISTRICT_HUBS[normalized_key]

        # Check prefix/first word (e.g. "Praha 10" -> "praha")
        first_word = normalized_key.split()[0] if normalized_key else ""
        if first_word in CZECH_DISTRICT_HUBS:
            return CZECH_DISTRICT_HUBS[first_word]

        # 2. Check offline postal code approximation
        zip_coords = approx_zip_coords(raw_key)
        if zip_coords:
            return zip_coords

        # 3. Check local disk cache
        if raw_key in self.cache:
            entry = self.cache[raw_key]
            return (entry["lat"], entry["lon"]) if entry else None

        # 4. Optional network query (only for user origin, never in loops)
        if allow_network:
            coords = self._query_nominatim(raw_key)
            if coords:
                self.cache[raw_key] = {"lat": coords[0], "lon": coords[1]}
            else:
                self.cache[raw_key] = None
            self._save_cache()
            return coords

        return None

    def _query_nominatim(self, query: str) -> Optional[Tuple[float, float]]:
        time.sleep(1.0)
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "SafePriceAggregator/1.0 (local-desktop-tool; safe-mode)"}
        params = {"q": f"{query}, Czech Republic", "format": "json", "limit": 1}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    return (float(data[0]["lat"]), float(data[0]["lon"]))
        except Exception:
            pass
        return None
