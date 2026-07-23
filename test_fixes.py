"""Test all crawler fixes WITHOUT Django setup."""
import importlib.util
import sys

# Import crawlers directly without Django
sys.path.insert(0, '/home/z/my-project/resume-job-crawler/core/crawlers')

# Load modules manually
for mod_name in ['jobvision_crawler', 'irantalent_crawler', 'estekhdam_crawler']:
    spec = importlib.util.spec_from_file_location(mod_name, f'/home/z/my-project/resume-job-crawler/core/crawlers/{mod_name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    globals()[mod_name] = mod

print("=" * 60)
print("TEST 1: JobVision - keyword INSIDE filters")
print("=" * 60)
try:
    results = jobvision_crawler.crawl_jobvision(keywords='python', time_range='7', max_pages=1)
    print(f"Results: {len(results)}")
    if results:
        r = results[0]
        print(f"First: {r['title']} | {r['company']} | {r['seniority_level']} | {r['posted_date']}")
        print(f"City: {r['city']}, Province: {r['province']}")
        print(f"Skills: {r['skills'][:3]}")
    else:
        print("NO RESULTS!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback; traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 2: IranTalent - lived_at time filter")
print("=" * 60)
try:
    results = irantalent_crawler.crawl_irantalent(keywords='python', time_range='7', max_pages=2)
    print(f"Results: {len(results)}")
    if results:
        r = results[0]
        print(f"First: {r['title']} | {r['company']} | {r['seniority_level']} | {r['posted_date']}")
        print(f"City: {r['city']}")
        print(f"Skills: {r['skills'][:3]}")
    else:
        print("NO RESULTS!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback; traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 3: E-estekhdam - 500 jobs, client filter")
print("=" * 60)
try:
    results = estekhdam_crawler.crawl_estekhdam(
        keywords='python',
        city='تهران',
        time_range='7',
        max_pages=3,
        client_filter_keywords=['python', 'برنامه', 'نرم افزار', 'توسعه'],
    )
    print(f"Results: {len(results)}")
    if results:
        r = results[0]
        print(f"First: {r['title']} | {r['company']} | {r['city']}")
        print(f"Skills: {r['skills'][:3]}")
    else:
        print("NO RESULTS (expected - API is broken)")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback; traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 4: JobVision time filter (1 day)")
print("=" * 60)
try:
    results = jobvision_crawler.crawl_jobvision(keywords='python', time_range='1', max_pages=3)
    print(f"Last 24h results: {len(results)}")
    if results:
        for r in results[:3]:
            print(f"  {r['title']} | {r['posted_date']}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("TEST 5: JobVision level filter (senior)")
print("=" * 60)
try:
    results = jobvision_crawler.crawl_jobvision(keywords='python', level='senior', time_range='30', max_pages=2)
    print(f"Senior results: {len(results)}")
    if results:
        for r in results[:3]:
            print(f"  {r['title']} | level={r['seniority_level']}")
except Exception as e:
    print(f"ERROR: {e}")

print("\nDONE")
