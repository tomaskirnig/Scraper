# Safe Price & Location Scraper 🏷️

Lokální etický vyhledávač / agregátor nabídek z českých bazarů a tržišť (**Bazoš.cz**, **Sbazar.cz**, **Aukro.cz**) s dynamickým filtrováním podle ceny a dojezdové vzdálenosti (km).

---

## 🛡️ Safe & Legal Architektura
Projekt je navržen tak, aby nemohl být označen za škodlivý nebo nelegální:
1. **Pouze veřejná data:** Žádné přihlašování, žádné kradení cookies, žádné obcházení CAPTCHA/hesel/paywallů.
2. **Polite rate limiting:** Pevná prodleva 1.0–2.0s s náhodným jitterem mezi požadavky na stejnou doménu.
3. **GDPR safe:** Scraper nesbírá osobní údaje (žádná telefonní čísla, jména ani e-maily prodejců).
4. **On-demand:** Dotazy se odesílají pouze když uživatel klikne "Vyhledat" pro konkrétní věc. Žádné masivní vysávání celých databází.
5. **Proč ne Facebook Marketplace?** FB vyžaduje přihlášení uživatele a blokuje anonymní čtení checkpointem. Obcházení ochran by porušilo etické/bezpečnostní zásady a vedlo k banu účtu/IP.

---

## 🚀 Rychlý start

### 1. Instalace závislostí
Projekt vyžaduje pouze:
```bash
pip install requests beautifulsoup4 streamlit pandas
```

### 2. Spuštění testu funkčnosti
```bash
python test_core.py
```

### 3. Spuštění webového rozhraní
```bash
streamlit run app.py
```
Aplikace se otevře v prohlížeči na adrese `http://localhost:8501`.

---

## 📁 Struktura projektu

- [`app.py`](file:///E:/VSCode/Personal_Projects/Scraper/app.py): Interaktivní Streamlit rozhraní (filtry, tabulka s prokliky, CSV export).
- [`core/models.py`](file:///E:/VSCode/Personal_Projects/Scraper/core/models.py): Datový model `Listing`.
- [`core/fetcher.py`](file:///E:/VSCode/Personal_Projects/Scraper/core/fetcher.py): `SafeFetcher` s rate limiterem a korektním User-Agentem.
- [`core/geo.py`](file:///E:/VSCode/Personal_Projects/Scraper/core/geo.py): Haversine vzdálenost (`math` stdlib) + offline mapa 70+ okresních měst a PSČ.
- [`core/aggregator.py`](file:///E:/VSCode/Personal_Projects/Scraper/core/aggregator.py): Sjednocení výsledků, výpočet vzdáleností a řazení.
- [`sources/`](file:///E:/VSCode/Personal_Projects/Scraper/sources): Adaptéry pro tržiště:
  - [`sources/bazos.py`](file:///E:/VSCode/Personal_Projects/Scraper/sources/bazos.py): Bazoš.cz
  - [`sources/sbazar.py`](file:///E:/VSCode/Personal_Projects/Scraper/sources/sbazar.py): Sbazar.cz (oficiální REST JSON API)
  - [`sources/aukro.py`](file:///E:/VSCode/Personal_Projects/Scraper/sources/aukro.py): Aukro.cz (SSR data cache / Schema.org)
- [`test_core.py`](file:///E:/VSCode/Personal_Projects/Scraper/test_core.py): Spustitelný self-check celého systému.
