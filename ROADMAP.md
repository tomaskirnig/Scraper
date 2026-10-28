# Safe Price & Location Scraper — Roadmap & Architecture

Projekt: Lokální agregátor veřejných nabídek podle dotazu, ceny a vzdálenosti.
Zásada: 100% legální, netoxický, neagresivní, bez obcházení ochran.

---

## 1. Safe & Legal Framework (Klíčový pilíř)

1. **Pouze veřejně přístupná data bez přihlášení:** Žádné obcházení paywallu, hesel ani tokenů.
2. **Žádné obcházení CAPTCHA / anti-bot ochran:** Pokud web hodí challenge, scraper nehackuje, ale požadavek zahodí.
3. **Respektování rate-limitingu:**
   - Pevný limit: min. 1.0–2.0s pauza mezi požadavky na stejnou doménu.
   - Náhodný jitter proti nárazovým vlnám.
4. **GDPR a osobní údaje:**
   - Scrapují se pouze metadata nabídky: Název, Cena, Lokalita, URL inzerátu, Obrázek.
   - ZÁKAZ stahování telefonních čísel, e-mailů a jmen prodejců.
5. **On-demand (ephemeral) dotazování:**
   - Žádné masivní vysávání celých databází do cloudu.
   - Dotaz běží pouze když uživatel klikne "Hledat" pro konkrétní věc.
6. **Transparentní User-Agent:**
   - Standardní prohlížečový header, žádné spoofování botnetů.
7. **Vyřazení Facebook Marketplace:**
   - FB striktně vyžaduje přihlášení a blokuje anonymní scraping checkpointem. Obcházení by porušilo zásadu legality a vedlo k banu účtu. Nahrazeno Aukrem.

---

## 2. Doporučený Tech Stack

- **Logika / Scraping:** Python 3 (`requests`, `beautifulsoup4`).
- **Geo / Vzdálenost:** stdlib `math` (Haversine vzorec) + offline centroidy okresů a PSČ. Žádné zdržování externími API v dávkách.
- **UI Interface:** `streamlit` (interaktivní formulář, dynamické řazení, tabulka s prokliky, CSV export).

---

## 3. Vývojová Roadmapa & Stav

### Fáze 1: Bezpečné jádro & Geo logika
- [x] Vytvořen datový model `Listing` ([`core/models.py`](file:///E:/VSCode/Personal_Projects/Scraper/core/models.py)).
- [x] Implementován `SafeFetcher` s rate-limitingem a jitterem ([`core/fetcher.py`](file:///E:/VSCode/Personal_Projects/Scraper/core/fetcher.py)).
- [x] Implementován `GeoResolver` s offline mapou 70+ okresů a PSČ + Haversine vzorec ([`core/geo.py`](file:///E:/VSCode/Personal_Projects/Scraper/core/geo.py)).
- [x] Spustitelný self-check ([`test_core.py`](file:///E:/VSCode/Personal_Projects/Scraper/test_core.py)).

### Fáze 2: Adaptéry tržišť
- [x] **Bazoš.cz:** Sestavení URL s cenou i nativní lokalitou `humkreis`/`hlokalita`, parsování HTML ([`sources/bazos.py`](file:///E:/VSCode/Personal_Projects/Scraper/sources/bazos.py)).
- [x] **Sbazar.cz:** Využití oficiálního veřejného REST JSON API Seznamu ([`sources/sbazar.py`](file:///E:/VSCode/Personal_Projects/Scraper/sources/sbazar.py)).
- [x] **Aukro.cz:** Bezpečné parsování SSR strukturovaných dat / Schema.org z HTML ([`sources/aukro.py`](file:///E:/VSCode/Personal_Projects/Scraper/sources/aukro.py)).

### Fáze 3: Streamlit UI
- [x] Vyhledávací formulář: Klíčové slovo, rozsah cen, výchozí město/PSČ, max vzdálenost v km ([`app.py`](file:///E:/VSCode/Personal_Projects/Scraper/app.py)).
- [x] Multiselect platforem (možnost zapnout/vypnout Bazoš, Sbazar, Aukro).
- [x] Řazení výsledků (nejlevnější, nejdražší, nejblíže, podle zdroje).
- [x] Interaktivní tabulka s náhledy fotografií a přímými odkazy na nabídky.
- [x] Export vyfiltrovaných výsledků do CSV.

### Fáze 4: Budoucí možná rozšíření
- [ ] Další bezpečné zdroje (např. Sbazar/Bazos Slovensko, Hyperinzerce, OdKarla).
- [ ] Ukládání oblíbených vyhledávání do lokální SQLite databáze.
