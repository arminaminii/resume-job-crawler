"""More E-estekhdam and IranTalent tests."""
import requests
import json

HEADERS_EE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Origin": "https://www.e-estekhdam.com",
    "Referer": "https://www.e-estekhdam.com/search/",
}

HEADERS_IT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.irantalent.com",
    "Referer": "https://www.irantalent.com/",
}

# ============ E-ESTEKHDAM: Does pagination work? ============
print("=" * 60)
print("E-ESTEKHDAM: Pagination test")
print("=" * 60)

all_ids = set()
for page in range(1, 11):
    try:
        r = requests.post(f"https://www.e-estekhdam.com/search-api/search?page={page}",
            json={}, headers=HEADERS_EE, timeout=15)
        d = r.json()
        jobs = d.get('data', [])
        ids = [j.get('id') for j in jobs]
        new_ids = set(ids) - all_ids
        all_ids.update(ids)
        titles = [j.get('title', '?')[:30] for j in jobs[:3]]
        print(f"  Page {page}: {len(jobs)} jobs, {len(new_ids)} new, total_unique={len(all_ids)}")
        if page <= 2:
            print(f"    Titles: {titles}")
        if not new_ids:
            print(f"  No new jobs, stopping")
            break
    except Exception as e:
        print(f"  Page {page}: ERROR {e}")
        break

print(f"\nTotal unique E-estekhdam jobs across all pages: {len(all_ids)}")

# ============ IRANTALENT: Test lived_at for time filtering ============
print("\n" + "=" * 60)
print("IRANTALENT: lived_at precision test")
print("=" * 60)

try:
    r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"keyword": "", "page": 1}, headers=HEADERS_IT, timeout=15)
    d = r.json()
    jobs = d.get('data', {}).get('data', [])
    print(f"No keyword: total={d.get('data',{}).get('total',0)}, page_jobs={len(jobs)}")
    print("\nFirst 10 jobs - created_at vs lived_at:")
    for j in jobs[:10]:
        print(f"  {j.get('title_farsi','?')[:35]:35s} | created_at={j.get('created_at','?'):12s} | lived_at={j.get('lived_at','?')}")
    
    # Check: jobs from last 1 day
    from datetime import datetime, timedelta, timezone
    IRAN_TZ = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(IRAN_TZ)
    one_day_ago = now - timedelta(days=1)
    
    recent_count = 0
    for j in jobs:
        lived = j.get('lived_at', '')
        if lived:
            try:
                # lived_at format: "2026-07-23 10:19:44"  
                dt = datetime.strptime(lived, '%Y-%m-%d %H:%M:%S').replace(tzinfo=IRAN_TZ)
                if dt >= one_day_ago:
                    recent_count += 1
            except:
                pass
    print(f"\nJobs from last 1 day (by lived_at): {recent_count}/{len(jobs)}")
    
    # Check: What if we use no keyword but large pages to get ALL jobs?
    total_all = d.get('data', {}).get('total', 0)
    print(f"\nTotal jobs with empty keyword: {total_all}")
    
    # Test with keyword=empty string vs no keyword
    r2 = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"page": 1}, headers=HEADERS_IT, timeout=15)
    d2 = r2.json()
    total2 = d2.get('data', {}).get('total', 0)
    print(f"Total jobs with NO keyword field: {total2}")
    
except Exception as e:
    print(f"ERROR: {e}")

# ============ IRANTALENT: Test category/job_category slug mapping ============
print("\n" + "=" * 60)
print("IRANTALENT: job_category slugs from actual data")
print("=" * 60)

try:
    r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"page": 1, "per_page": 30}, headers=HEADERS_IT, timeout=15)
    d = r.json()
    jobs = d.get('data', {}).get('data', [])
    
    all_cat_slugs = set()
    for j in jobs:
        for cat in (j.get('job_category') or []):
            if isinstance(cat, dict) and cat.get('slug'):
                all_cat_slugs.add(cat['slug'])
    
    print(f"Found {len(all_cat_slugs)} unique category slugs in page 1:")
    for s in sorted(all_cat_slugs):
        print(f"  - {s}")
except Exception as e:
    print(f"ERROR: {e}")

print("\nDONE")
