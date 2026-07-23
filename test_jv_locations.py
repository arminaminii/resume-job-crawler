import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://jobvision.ir",
    "Referer": "https://jobvision.ir/",
}

BASE = "https://candidateapi.jobvision.ir/api/v1"

# 1. Try location list endpoint
print("=== Test Location Endpoints ===")
for ep in ["Location/GetAllProvinces", "Location/GetAllCities",
          "JobPost/GetAllProvinces", "location/provinces",
          "FilterData/GetProvinces", "FilterData/GetCities"]:
    url = f"{BASE}/{ep}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"GET {ep}: {r.status_code} | {r.text[:200]}")
    except Exception as e:
        print(f"GET {ep}: ERROR {e}")

# 2. Try POST for location data
print("\n=== POST Location Endpoints ===")
for ep in ["Location/GetAllProvinces", "Location/GetAllCities",
          "FilterData/GetProvinces", "FilterData/GetCities"]:
    for base in [BASE, "https://candidateapi.jobvision.ir"]:
        url = f"{base}/{ep}"
        try:
            r = requests.post(url, json={}, headers=HEADERS, timeout=10)
            if r.status_code == 200 and len(r.text) > 10:
                print(f"POST {base}/{ep}: {r.status_code} | {r.text[:300]}")
        except Exception as e:
            pass

# 3. Try getting city list for Tehran province
print("\n=== Tehran City Slug Test ===")
# From the province slug pattern: 'in-all-cities-of-tehran'
# Try to get cities of a specific province
payloads = [
    {"page": 1, "pageSize": 10, "sort": 0, "filters": {"locationSlugs": ["in-all-cities-of-tehran"]}},
    {"page": 1, "pageSize": 10, "sort": 0, "filters": {"locationSlugs": ["in-all-cities-of-tehran"]}, "keyword": "python"},
    {"page": 1, "pageSize": 50, "sort": 0, "filters": {}}, "keyword": "python",
]
for i, p in enumerate(payloads):
    try:
        r = requests.post(f"{BASE}/JobPost/List", json=p, headers=HEADERS, timeout=15)
        d = r.json()
        jobs = d.get('data', {}).get('jobPosts', [])
        cities = set()
        for j in jobs:
            loc = j.get('location', {}) or {}
            city = loc.get('city', {}) or {}
            city_name = city.get('titleFa', '') or city.get('name', '')
            if city_name:
                cities.add(city_name)
        total = d.get('data', {}).get('jobPostCount', 0)
        print(f"Test {i}: total={total}, unique cities: {len(cities)}")
        for c in sorted(cities):
            print(f"  {c}")
    except Exception as e:
        print(f"Test {i}: ERROR {e}")

# 4. Check if there's a city list API with slug
print("\n=== Specific City Slug Tests ===")
for slug in ['tehran', 'isfahan', 'alborz-karaj', 'tehran-pars', 'tehran-shemiran']:
    payload = {"page": 1, "pageSize": 5, "sort": 0, "filters": {"locationSlugs": [slug]}}
    try:
        r = requests.post(f"{BASE}/JobPost/List", json=payload, headers=HEADERS, timeout=10)
        d = r.json()
        total = d.get('data', {}).get('jobPostCount', 0)
        jobs = d.get('data', {}).get('jobPosts', [])
        print(f"slug='{slug}': total={total}, jobs_on_page={len(jobs)}")
    except Exception as e:
        print(f"slug='{slug}': ERROR {e}")

print("\nDONE")
