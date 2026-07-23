"""More API tests."""
import requests
import json

HEADERS_IT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.irantalent.com",
    "Referer": "https://www.irantalent.com/",
}

HEADERS_EE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}

# ============ IRANTALENT: Test slug vs keyword ============
print("=" * 60)
print("IRANTALENT: slug parameter test")
print("=" * 60)

# Test with various slugs
slugs_to_test = [
    ("programming", "programming"),
    ("web-development", "web-development"),
    ("python", "python"),
    ("frontend", "frontend"),
    ("backend", "backend"),
    ("devops", "devops"),
]

for slug_val, label in slugs_to_test:
    try:
        r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
            json={"slug": slug_val, "page": 1}, headers=HEADERS_IT, timeout=15)
        d = r.json()
        resp_data = d.get('data', {})
        if isinstance(resp_data, dict):
            total = resp_data.get('total', 0)
        else:
            total = len(resp_data)
        print(f"  slug={slug_val:20s} → total={total}")
    except Exception as e:
        print(f"  slug={slug_val:20s} → ERROR: {e}")

# Test: both slug AND keyword together
print("\n--- slug + keyword together ---")
try:
    r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"slug": "programming", "keyword": "python", "page": 1}, headers=HEADERS_IT, timeout=15)
    d = r.json()
    resp_data = d.get('data', {})
    if isinstance(resp_data, dict):
        total = resp_data.get('total', 0)
        jobs = resp_data.get('data', [])
    else:
        total = len(resp_data)
        jobs = resp_data
    print(f"  slug=programming, keyword=python → total={total}, first 3 titles:")
    for j in jobs[:3]:
        print(f"    - {j.get('title_farsi', j.get('title', 'N/A'))}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test: get all keys of first job to find more date fields
print("\n--- IranTalent: all keys of first job ---")
try:
    r = requests.post("https://api.irantalent.com/api/v1/employer/position/search-by-slug",
        json={"slug": "programming", "page": 1}, headers=HEADERS_IT, timeout=15)
    d = r.json()
    jobs = d.get('data', {}).get('data', [])
    if jobs:
        for k, v in jobs[0].items():
            print(f"  {k}: {str(v)[:100]}")
except Exception as e:
    print(f"ERROR: {e}")

# ============ E-ESTEKHDAM: Try HTML scraping ============
print("\n" + "=" * 60)
print("E-ESTEKHDAM: HTML scraping test")
print("=" * 60)

# Test their search page HTML
urls_to_test = [
    "https://www.e-estekhdam.com/search/?q=python",
    "https://www.e-estekhdam.com/search/?q=برنامه",
    "https://www.e-estekhdam.com/search/",
    "https://www.e-estekhdam.com/jobs/",
]

for url in urls_to_test:
    try:
        r = requests.get(url, headers=HEADERS_EE, timeout=15)
        print(f"\nGET {url}")
        print(f"  Status: {r.status_code}, Length: {len(r.text)}")
        # Check if it has job listings in HTML
        if 'job' in r.text.lower() or 'آگهی' in r.text or 'استخدام' in r.text:
            # Extract a few snippets around job titles
            import re
            # Find any JSON data embedded in HTML (Next.js, etc.)
            scripts = re.findall(r'<script[^>]*>\s*(\{.*?\})\s*</script>', r.text, re.DOTALL)
            if scripts:
                print(f"  Found {len(scripts)} embedded JSON scripts")
                for i, s in enumerate(scripts[:2]):
                    try:
                        parsed = json.loads(s)
                        print(f"  Script {i} keys: {list(parsed.keys())[:10]}")
                    except:
                        print(f"  Script {i}: not valid JSON ({len(s)} chars)")
            else:
                print(f"  No embedded JSON found")
                # Check for Next.js data
                if '__NEXT_DATA__' in r.text:
                    print(f"  Has __NEXT_DATA__!")
                    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
                    if match:
                        nd = json.loads(match.group(1))
                        print(f"  NEXT_DATA keys: {list(nd.keys())}")
                        # Look for jobs in the data
                        props = nd.get('props', {})
                        page_props = props.get('pageProps', {})
                        print(f"  pageProps keys: {list(page_props.keys())}")
                        for k, v in page_props.items():
                            if isinstance(v, list):
                                print(f"    {k}: list of {len(v)}")
                            elif isinstance(v, dict):
                                print(f"    {k}: dict with keys {list(v.keys())[:5]}")
                            else:
                                print(f"    {k}: {str(v)[:100]}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Also test e-estekhdam search API with GET
print("\n--- E-estekhdam: GET search-api ---")
try:
    r = requests.get("https://www.e-estekhdam.com/search-api/search?q=python&page=1", headers=HEADERS_EE, timeout=15)
    print(f"  GET search-api/search?q=python: {r.status_code} - {r.text[:200]}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\nDONE")
