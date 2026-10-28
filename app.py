import streamlit as st
import pandas as pd
from core.aggregator import SafeAggregator

st.set_page_config(
    page_title="Safe Price & Location Aggregator",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Palette from Image:
# 272838: Shadow Grey (Dark Base)
# F3DE8A: Light Gold (Primary Accent / Headers / Badges)
# EB9486: Sweet Salmon (Buttons / Focus / Active Controls)
# 7E7F9A: Lavender Grey (Borders / Muted Elements / Secondary)

st.markdown("""
<style>
    /* 1. Global Dark Theme & Palette */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #272838 !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #1e1f2c !important;
        border-right: 1px solid rgba(126, 127, 154, 0.3) !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. Headings & Text */
    h1, h2, h3, .stApp h1, .stApp h2 {
        color: #F3DE8A !important; /* Light Gold */
        font-weight: 700 !important;
    }

    .stCaption, p, label, [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }

    /* 3. STRICT 4PX BORDER RADIUS ON ALL ELEMENTS */
    html body button,
    html body [data-testid^="stBaseButton"],
    html body [data-testid^="baseButton"],
    html body .stButton > button,
    html body .stDownloadButton > button,
    html body div[data-baseweb="input"],
    html body div[data-baseweb="input"] > div,
    html body div[data-baseweb="base-input"],
    html body div[data-baseweb="base-input"] > div,
    html body input,
    html body div[data-baseweb="select"],
    html body div[data-baseweb="select"] > div,
    html body div[data-baseweb="tag"],
    html body span[data-baseweb="tag"],
    html body div[data-testid="stExpander"],
    html body div[data-testid="stExpander"] details,
    html body div[data-testid="stExpander"] summary,
    html body div[data-testid="stMetric"],
    html body div[data-testid="stAlert"],
    html body div[data-testid="stDataFrame"],
    html body div[data-testid="stNumberInput"] button,
    html body div[data-baseweb="slider"] div[role="slider"] {
        border-radius: 4px !important;
    }

    /* 4. Primary Button (Sweet Salmon #EB9486) */
    html body button[kind="primary"],
    html body .stButton > button {
        background-color: #EB9486 !important;
        color: #272838 !important; /* Shadow Grey high-contrast text */
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: 1px solid #EB9486 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
        transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    html body button[kind="primary"]:hover,
    html body .stButton > button:hover {
        background-color: #e28475 !important;
        border-color: #e28475 !important;
        box-shadow: 0 0 16px rgba(235, 148, 134, 0.55) !important;
    }

    /* 5. Download / Secondary Button */
    html body .stDownloadButton > button {
        background-color: #2f3042 !important;
        color: #F3DE8A !important; /* Gold text */
        border: 1px solid #7E7F9A !important;
        font-weight: 600 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
    }

    html body .stDownloadButton > button:hover {
        background-color: #393a50 !important;
        border-color: #EB9486 !important;
        box-shadow: 0 0 12px rgba(235, 148, 134, 0.35) !important;
    }

    /* 6. Inputs (Text, Number, Select containers) */
    html body div[data-baseweb="input"],
    html body div[data-baseweb="input"] > div,
    html body div[data-baseweb="base-input"],
    html body div[data-baseweb="select"] > div {
        background-color: #2f3042 !important;
        border: 1px solid #7E7F9A !important;
        color: #ffffff !important;
    }

    html body input {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    html body div[data-baseweb="input"]:focus-within,
    html body div[data-baseweb="select"] > div:focus-within {
        border-color: #EB9486 !important;
        box-shadow: 0 0 0 1px #EB9486 !important;
    }

    /* Plus/Minus number buttons */
    html body div[data-testid="stNumberInput"] button {
        background-color: #242535 !important;
        border: 1px solid #7E7F9A !important;
        color: #F3DE8A !important;
    }

    html body div[data-testid="stNumberInput"] button:hover {
        border-color: #EB9486 !important;
        color: #EB9486 !important;
    }

    /* 7. Multiselect Tags (#7E7F9A background + #F3DE8A text + #EB9486 remove icon) */
    html body div[data-baseweb="tag"],
    html body span[data-baseweb="tag"] {
        background-color: rgba(126, 127, 154, 0.35) !important;
        color: #F3DE8A !important;
        border: 1px solid #7E7F9A !important;
    }

    html body div[data-baseweb="tag"] span {
        color: #F3DE8A !important;
        font-weight: 500 !important;
    }

    html body div[data-baseweb="tag"] svg {
        fill: #EB9486 !important;
    }

    /* 8. Slider (Sweet Salmon thumb + Gold highlight) */
    html body div[data-baseweb="slider"] div[role="slider"] {
        background-color: #EB9486 !important;
        border: 2px solid #F3DE8A !important;
        box-shadow: 0 0 10px rgba(235, 148, 134, 0.6) !important;
    }

    html body div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        color: #F3DE8A !important;
        font-weight: 700 !important;
    }

    /* 9. Checkbox */
    html body div[data-testid="stCheckbox"] label span[role="checkbox"][aria-checked="true"] {
        background-color: #EB9486 !important;
        border-color: #EB9486 !important;
    }

    /* 10. Expander Card */
    html body div[data-testid="stExpander"],
    html body div[data-testid="stExpander"] details {
        background-color: #2f3042 !important;
        border: 1px solid #7E7F9A !important;
    }

    html body div[data-testid="stExpander"] summary {
        color: #F3DE8A !important;
        font-weight: 600 !important;
    }

    /* 11. Metric Cards */
    html body div[data-testid="stMetric"] {
        background-color: #2f3042 !important;
        border: 1px solid rgba(126, 127, 154, 0.4) !important;
        padding: 12px 18px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }

    html body div[data-testid="stMetric"] label {
        color: #7E7F9A !important;
        font-size: 0.85rem !important;
    }

    html body div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #F3DE8A !important;
        font-weight: 700 !important;
    }

    /* 12. Hero Badge (Light Gold #F3DE8A) */
    .hero-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #272838 !important;
        background-color: #F3DE8A !important;
        border: 1px solid #e5d078 !important;
        padding: 3px 10px;
        border-radius: 4px !important;
        margin-bottom: 8px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    }

    /* 13. Dataframe Table Styling */
    html body div[data-testid="stDataFrame"] {
        border: 1px solid rgba(126, 127, 154, 0.35) !important;
        background-color: #2f3042 !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom header
st.markdown('<div class="hero-badge">Verified Safe & Legal Scraper</div>', unsafe_allow_html=True)
st.title("🏷️ Safe Price & Location Aggregator")
st.caption("Etický vyhledávač veřejných nabídek v ČR (Bazoš, Sbazar, Aukro) s filtrem podle ceny a dojezdové vzdálenosti.")

# Sidebar / Filters
with st.sidebar:
    st.header("⚙️ Parametry vyhledávání")
    
    query = st.text_input("Dotaz / Hledané zboží", value="iPhone 13", placeholder="např. iPhone 13, kolo, stůl...")
    
    col1, col2 = st.columns(2)
    with col1:
        min_price = st.number_input("Cena od (Kč)", min_value=0, value=1000, step=500)
    with col2:
        max_price = st.number_input("Cena do (Kč)", min_value=0, value=15000, step=500)

    st.subheader("📍 Geografický filtr")
    origin_place = st.text_input("Výchozí město nebo PSČ", value="Ostrava", placeholder="např. Ostrava, Brno, 702 00...")
    max_distance_km = st.slider("Max vzdálenost (km)", min_value=0, max_value=300, value=50, step=10, 
                               help="0 = bez omezení vzdálenosti (celá ČR)")
    
    include_nationwide = st.checkbox("Zahrnout nabídky s doručením (ČR)", value=True,
                                     help="Ponechá nabídky z Aukra a inzeráty s možností zaslání poštou/kurýrem.")

    st.subheader("🌐 Zdroje dat")
    available_sources = ["Bazoš", "Sbazar", "Aukro"]
    selected_sources = st.multiselect("Vyberte platformy", options=available_sources, default=available_sources)

    st.divider()
    with st.expander("🛡️ Safe & Legal záruky"):
        st.markdown("""
        - **100% veřejná data:** Žádné přihlašování, žádné obcházení CAPTCHA/hesel.
        - **Polite Rate Limiting:** 1–2s prodleva mezi požadavky s náhodným jitterem.
        - **GDPR Safe:** Žádný sběr telefonů, jmen ani e-mailů.
        - **Proč ne Facebook Marketplace?** FB vyžaduje přihlášení a blokuje scrapery. Obcházení by bylo nelegální a riskantní.
        """)

# Initialize Aggregator
@st.cache_resource
def get_aggregator():
    return SafeAggregator()

aggregator = get_aggregator()

# Search button trigger
search_clicked = st.button("🔍 Vyhledat nabídky", type="primary", use_container_width=True)

if search_clicked or st.session_state.get("has_searched", False):
    st.session_state["has_searched"] = True
    
    if not query.strip():
        st.warning("Zadejte prosím hledaný výraz.")
    elif not selected_sources:
        st.warning("Vyberte alespoň jeden zdroj.")
    else:
        with st.spinner(f"Bezpečně prohledávám vybrané zdroje ({', '.join(selected_sources)})..."):
            results = aggregator.search(
                query=query.strip(),
                min_price=min_price if min_price > 0 else None,
                max_price=max_price if max_price > 0 else None,
                origin_place=origin_place.strip() if origin_place else None,
                max_distance_km=max_distance_km if max_distance_km > 0 else None,
                enabled_sources=selected_sources,
                include_nationwide=include_nationwide
            )

        if not results:
            st.info("Nebyly nalezeny žádné nabídky odpovídající zadaným kritériím.")
        else:
            # Summary Metrics Row
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Celkem nalezeno", f"{len(results)} inzerátů")
            with m2:
                valid_prices = [r.price for r in results if r.price and r.price > 0]
                min_p = f"{int(min(valid_prices)):,} Kč".replace(",", " ") if valid_prices else "N/A"
                st.metric("Nejnižší cena", min_p)
            with m3:
                st.metric("Výchozí lokalita", f"{origin_place} (max {max_distance_km} km)")

            # Sorting controls
            sort_col1, sort_col2 = st.columns([3, 1])
            with sort_col2:
                sort_option = st.selectbox(
                    "Řazení výsledků",
                    options=["Nejlevnější", "Nejdražší", "Nejblíže (km)", "Zdroj"]
                )

            # Sort items
            if sort_option == "Nejlevnější":
                results.sort(key=lambda x: (x.price is None, x.price or 0))
            elif sort_option == "Nejdražší":
                results.sort(key=lambda x: (x.price is None, -(x.price or 0)))
            elif sort_option == "Nejblíže (km)":
                results.sort(key=lambda x: (x.distance_km is None, x.distance_km or 99999))
            elif sort_option == "Zdroj":
                results.sort(key=lambda x: x.source)

            # Prepare DataFrame for Streamlit display
            table_data = []
            for item in results:
                dist_str = f"{item.distance_km} km" if item.distance_km is not None else "Neuvedeno / ČR"
                table_data.append({
                    "Náhled": item.image_url or "",
                    "Název": item.title,
                    "Cena": item.price_display,
                    "Lokalita": item.location or "ČR",
                    "Vzdálenost": dist_str,
                    "Zdroj": item.source,
                    "Odkaz": item.url
                })

            df = pd.DataFrame(table_data)

            # Interactive table with clickable link column and images
            st.dataframe(
                df,
                column_config={
                    "Náhled": st.column_config.ImageColumn("Foto", help="Náhledový obrázek"),
                    "Odkaz": st.column_config.LinkColumn("Odkaz na inzerát", display_text="Otevřít nabídku ↗"),
                    "Cena": st.column_config.TextColumn("Cena"),
                    "Vzdálenost": st.column_config.TextColumn("Vzdálenost od výchozího bodu"),
                },
                hide_index=True,
                use_container_width=True
            )

            # CSV Export button
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Stáhnout výsledky jako CSV",
                data=csv_data,
                file_name=f"nabidky_{query.strip().replace(' ', '_')}.csv",
                mime="text/csv",
            )
