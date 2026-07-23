"""Direct API testing to understand real behavior."""
import requests
import json

HEADERS_JV = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://jobvision.ir",
    "Referer": "https://jobvision.ir/",
}

HEADERS_IT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.irantalent.com",
    "Referer": "https://www.irantalent.com/",
}

HEADERS_EE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Origin": "https://www.e-estekhdam.com",
    "Referer": "https://www.e-estekhdam.com/search/",
}

# ============ JOBVISION ============
print("=" * 60)
print("JOBVISION TEST")
print("=" * 60)

# Test 1: keyword inside filters (as crawl-py does)
print("\n--- Test 1: keyword INSIDE filters ---")
payload1 = {
    "page": 1,
    "pageSize": 10,
    "sort": 0,
    "filters": {"keyword": "python"},
}
try:
    r = requests.post("https://candidateapi.jobvision.ir/api/v1/JobPost/List", json=payload1, headers=HEADERS_JV, timeout=15)
    d = r.json()
    total = d.get('data', {}).get('jobPostCount', 0)
    jobs = d.get('data', {}).get('jobPosts', [])
    print(f"Total: {total}, Page jobs: {len(jobs)}")
    if jobs:
        j = jobs[0]
        print(f"First job: {j.get('title', 'N/A')}")
        act = j.get('activationTime', {})
        print(f"activationTime: {json.dumps(act, ensure_ascii=False)}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: keyword at top-level (as our current code does)
print("\n--- Test 2: keyword at TOP-LEVEL ---")
payload2 = {
    "page": 1,
    "pageSize": 10,
    "sort": 1,
    "keyword": "python",
    "filters": {},
}
try:
    r = requests.post("https://candidateapi.jobvision.ir/api/v1/JobPost/List", json=payload2, headers=HEADERS_JV, timeout=15)
    d = r.json()
    total = d.get('data', {}).get('jobPostCount', 0)
    jobs = d.get('data', {}).get('jobPosts', [])
    print(f"Total: {total}, Page jobs: {len(jobs)}")
    if jobs:
        j = jobs[0]
        print(f"First job: {j.get('title', 'N/A')}")
except Exception as e:
    print(f"ERROR: {e}")

# ============ IRANTALENT ============
print("\n" + "=" * 60)
print("IRANTALENT TEST")
print("=" * 60)

# Test with different params to see which ones work
print("\n--- Test 1: keyword=python ---")
try:
    r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"keyword": "python", "page": 1}, headers=HEADERS_IT, timeout=15)
    d = r.json()
    resp_data = d.get('data', {})
    if isinstance(resp_data, dict):
        jobs = resp_data.get('data', [])
        total = resp_data.get('total', 0)
        last = resp_data.get('last_page', 1)
    else:
        jobs = resp_data
        total = len(resp_data)
        last = 1
    print(f"Total: {total}, last_page: {last}, page jobs: {len(jobs)}")
    if jobs:
        j = jobs[0]
        print(f"First job keys: {list(j.keys())[:15]}")
        print(f"Title: {j.get('title_farsi', j.get('title', 'N/A'))}")
        print(f"created_at: {j.get('created_at', 'N/A')}")
        print(f"slug: {j.get('slug', 'N/A')}")
        # Check for date-related fields
        for k in j.keys():
            if 'date' in k.lower() or 'time' in k.lower() or 'creat' in k.lower() or 'publish' in k.lower():
                print(f"  {k}: {j[k]}")
except Exception as e:
    print(f"ERROR: {e}")

# Test: category slug
print("\n--- Test 2: slug=programming ---")
try:
    r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"slug": "programming", "page": 1}, headers=HEADERS_IT, timeout=15)
    d = r.json()
    resp_data = d.get('data', {})
    if isinstance(resp_data, dict):
        jobs = resp_data.get('data', [])
        total = resp_data.get('total', 0)
    else:
        jobs = resp_data
        total = len(resp_data)
    print(f"Total: {total}, page jobs: {len(jobs)}")
except Exception as e:
    print(f"ERROR: {e}")

# Test: per_page param
print("\n--- Test 3: keyword=python, per_page=50 ---")
try:
    r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"keyword": "python", "page": 1, "per_page": 50}, headers=HEADERS_IT, timeout=15)
    d = r.json()
    resp_data = d.get('data', {})
    if isinstance(resp_data, dict):
        jobs = resp_data.get('data', [])
        total = resp_data.get('total', 0)
    else:
        jobs = resp_data
        total = len(resp_data)
    print(f"Total: {total}, page jobs: {len(jobs)}")
except Exception as e:
    print(f"ERROR: {e}")

# ============ E-ESTEKHDAM ============
print("\n" + "=" * 60)
print("E-ESTEKHDAM TEST")
print("=" * 60)

# Test 1: basic search
print("\n--- Test 1: q=python ---")
try:
    r = requests.post("https://www.e-estekhdam.com/search-api/search?page=1",
        json={"q": "python"}, headers=HEADERS_EE, timeout=15)
    d = r.json()
    print(f"ok: {d.get('ok')}, data count: {len(d.get('data', []))}")
    jobs = d.get('data', [])
    if jobs:
        j = jobs[0]
        print(f"First job keys: {list(j.keys())}")
        print(f"Title: {j.get('title', 'N/A')}")
        print(f"All fields: {json.dumps(j, ensure_ascii=False)[:500]}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: empty body
print("\n--- Test 2: empty body ---")
try:
    r = requests.post("https://www.e-estekhdam.com/search-api/search?page=1",
        json={}, headers=HEADERS_EE, timeout=15)
    d = r.json()
    print(f"ok: {d.get('ok')}, data count: {len(d.get('data', []))}")
    jobs = d.get('data', [])
    if jobs:
        j = jobs[0]
        print(f"First job title: {j.get('title', 'N/A')}")
        print(f"promoted: {j.get('promoted', 'N/A')}")
        # Check all keys of first 3 jobs
        for i, job in enumerate(jobs[:3]):
            print(f"  Job {i}: {job.get('title', 'N/A')} | promoted={job.get('promoted')} | keys={list(job.keys())}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 3: different API endpoints
print("\n--- Test 3: Try /api/jobs endpoint ---")
for endpoint in [
    "https://www.e-estekhdam.com/api/jobs",
    "https://www.e-estekhdam.com/api/v1/jobs",
    "https://www.e-estekhdam.com/api/search",
    "https://www.e-estekhdam.com/search-api/jobs",
]:
    try:
        r = requests.get(endpoint, headers=HEADERS_EE, timeout=10)
        print(f"  GET {endpoint}: {r.status_code}")
        if r.status_code == 200:
            print(f"    Response: {r.text[:200]}")
    except Exception as e:
        print(f"  GET {endpoint}: ERROR {e}")

# Test 4: POST to different endpoints
print("\n--- Test 4: Try POST to /api/jobs ---")
for endpoint in [
    "https://www.e-estekhdam.com/api/jobs",
    "https://www.e-estekhdam.com/api/v1/jobs",
]:
    try:
        r = requests.post(endpoint, json={"q": "python"}, headers=HEADERS_EE, timeout=10)
        print(f"  POST {endpoint}: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"  POST {endpoint}: ERROR {e}")

# Test 5: Check if e-estekhdam has a different search page API
print("\n--- Test 5: Try search with more params ---")
for body in [
    {"q": "python", "page_size": 20},
    {"keyword": "python"},
    {"search": "python"},
    {"title": "python"},
]:
    try:
        r = requests.post("https://www.e-estekhdam.com/search-api/search?page=1",
            json=body, headers=HEADERS_EE, timeout=10)
        d = r.json()
        jobs = d.get('data', [])
        titles = [j.get('title', '?')[:30] for j in jobs[:3]]
        print(f"  Body {body}: {len(jobs)} jobs, titles={titles}")
    except Exception as e:
        print(f"  Body {body}: ERROR {e}")

print("\nDONE")
