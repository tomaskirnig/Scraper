import sys
from core.models import Listing
from core.geo import haversine_km, GeoResolver
from core.fetcher import SafeFetcher
from core.aggregator import SafeAggregator

def test_haversine():
    # Prague to Brno is approx 185-210 km
    prague = (50.0875, 14.4213)
    brno = (49.1951, 16.6068)
    dist = haversine_km(prague[0], prague[1], brno[0], brno[1])
    assert 180 <= dist <= 210, f"Expected ~195km, got {dist}"
    print(f"Haversine test passed: Prague to Brno = {dist} km")

def test_geo_resolver():
    geo = GeoResolver()
    coords = geo.get_coords("Brno")
    assert coords is not None, "Brno should be resolved from pre-seeded hubs"
    assert round(coords[0], 1) == 49.2
    print(f"GeoResolver test passed: Brno = {coords}")

def test_aggregator_search():
    agg = SafeAggregator()
    # Search for something very common with safe delay
    print("Testing aggregator with query 'stul' on Bazoš, Sbazar, Aukro...")
    results = agg.search(
        query="stul",
        min_price=100,
        max_price=2000,
        origin_place="Ostrava",
        max_distance_km=100,
        enabled_sources=["Bazoš", "Sbazar", "Aukro"]
    )
    assert len(results) > 0, "Aggregator should return at least 1 item"
    print(f"Aggregator test passed: found {len(results)} items")
    for r in results[:3]:
        print(f"  [{r.source}] {r.title} | {r.price_display} | {r.location} | {r.distance_km} km")

if __name__ == "__main__":
    test_haversine()
    test_geo_resolver()
    test_aggregator_search()
    print("ALL CHECKS PASSED.")
