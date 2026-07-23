import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://jobvision.ir",
    "Referer": "https://jobvision.ir/",
}

API = "https://candidateapi.jobvision.ir/api/v1/JobPost/List"

# Test ALL possible keyword placements
tests = [
    {"name": "1. keyword at top-level", "payload": {"page": 1, "pageSize": 10, "sort": 0, "filters": {}, "keyword": "python"}},
    {"name": "2. keyword in filters", "payload": {"page": 1, "pageSize": 10, "sort": 0, "filters": {"keyword": "python"}}},
    {"name": "3. BOTH", "payload": {"page": 1, "pageSize": 10, "sort": 0, "keyword": "python", "filters": {"keyword": "python"}}},
    {"name": "4. no keyword (all)", "payload": {"page": 1, "pageSize": 10, "sort": 0, "filters": {}}},
    {"name": "5. filters.keyword with sort=1", "payload": {"page": 1, "pageSize": 10, "sort": 1, "filters": {"keyword": "python"}}},
    {"name": "6. top-level sort=1", "payload": {"page": 1, "pageSize": 10, "sort": 1, "keyword": "python", "filters": {}}},
]

for test in tests:
    try:
        r = requests.post(API, json=test["payload"], headers=HEADERS, timeout=15)
        d = r.json()
        total = d.get('data', {}).get('jobPostCount', 0)
        jobs = d.get('data', {}).get('jobPosts', [])
        first_title = jobs[0].get('title', '?')[:40] if jobs else 'N/A'
        # Check if first 3 titles contain 'python' or 'پایتون'
        py_count = 0
        for j in jobs[:5]:
            t = (j.get('title', '') or '').lower()
            if 'python' in t or 'پایتون' in t:
                py_count += 1
        print(f"{test['name']:35s} total={total:>6}, py_in_5={py_count}, first={first_title}")
    except Exception as e:
        print(f"{test['name']:35s} ERROR: {e}")

# Also test what crawl-py actually sends by simulating their exact code
print("\n--- crawl-py exact format ---")
payload = {
    "page": 1,
    "pageSize": 10,
    "sort": 0,
    "filters": {"keyword": "Product Manager"},
}
try:
    r = requests.post(API, json=payload, headers=HEADERS, timeout=15)
    d = r.json()
    total = d.get('data', {}).get('jobPostCount', 0)
    jobs = d.get('data', {}).get('jobPosts', [])
    pm_count = 0
    for j in jobs[:5]:
        t = (j.get('title', '') or '').lower()
        if 'product' in t or 'محصول' in t or 'مدیر محصول' in t:
            pm_count += 1
    print(f"crawl-py format: total={total}, pm_in_5={pm_count}")
    for j in jobs[:3]:
        print(f"  {j.get('title', '?')[:50]}")
except Exception as e:
    print(f"ERROR: {e}")

# Test with Persian keyword
print("\n--- Persian keyword test ---")
for kw in ['پایتون', 'دجانگو', 'react']:
    for placement in ['top', 'filter']:
        if placement == 'top':
            payload = {"page": 1, "pageSize": 10, "sort": 0, "filters": {}, "keyword": kw}
        else:
            payload = {"page": 1, "pageSize": 10, "sort": 0, "filters": {"keyword": kw}}
        try:
            r = requests.post(API, json=payload, headers=HEADERS, timeout=15)
            d = r.json()
            total = d.get('data', {}).get('jobPostCount', 0)
            print(f"  kw='{kw}' ({placement:6s}): total={total}")
        except:
            pass

# Test: what if we send searchKeyword instead of keyword?
print("\n--- Alternative field names ---")
for field in ['searchKeyword', 'titleKeyword', 'search_keyword', 'q', 'query']:
    payload = {"page": 1, "pageSize": 10, "sort": 0, "filters": {field: "python"}}
    try:
        r = requests.post(API, json=payload, headers=HEADERS, timeout=15)
        d = r.json()
        total = d.get('data', {}).get('jobPostCount', 0)
        if total != 43663:  # Different from baseline (all jobs)
            print(f"  {field}: total={total} *** DIFFERENT ***")
        else:
            print(f"  {field}: total={total}")
    except:
        pass
