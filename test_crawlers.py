"""
Direct test script for crawlers - run this to verify they work outside Django.
Usage:  python test_crawlers.py
"""
import sys
import os
import logging

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
)


def test_jobvision():
    """Test Jobvision REST API crawler directly."""
    print("\n" + "="*60)
    print("TEST 1: Jobvision REST API Crawler")
    print("="*60)

    from core.crawlers.jobvision_crawler import crawl_jobvision

    results = crawl_jobvision(
        keywords='python developer',
        city='تهران',
        level='all',
        time_range='30',
        max_pages=1,
        category_slugs=['developer'],
    )

    print(f"\nResults: {len(results)} jobs found")
    if results:
        print(f"\nFirst result:")
        r = results[0]
        print(f"  Title: {r.get('title', 'N/A')}")
        print(f"  Company: {r.get('company', 'N/A')}")
        print(f"  City: {r.get('city', 'N/A')}")
        print(f"  Salary: {r.get('salary', 'N/A')}")
        print(f"  URL: {r.get('url', 'N/A')}")
        print(f"  Skills: {r.get('skills', [])}")
        print(f"  Remote: {r.get('remote', False)}")
    else:
        print("  No results! Check your internet connection and API availability.")

    return len(results) > 0


def test_jobvision_no_category():
    """Test Jobvision without category slugs (keyword-only search)."""
    print("\n" + "="*60)
    print("TEST 2: Jobvision - keyword only (no category slugs)")
    print("="*60)

    from core.crawlers.jobvision_crawler import crawl_jobvision

    results = crawl_jobvision(
        keywords='python',
        city='',
        level='all',
        time_range='30',
        max_pages=1,
        category_slugs=[],
    )

    print(f"\nResults: {len(results)} jobs found")
    return len(results) > 0


def test_estekhdam():
    """Test E-estekhdam REST API crawler."""
    print("\n" + "="*60)
    print("TEST 3: E-estekhdam REST API Crawler")
    print("="*60)

    from core.crawlers.estekhdam_crawler import crawl_estekhdam

    results = crawl_estekhdam(
        keywords='python',
        city='تهران',
        level='all',
        time_range='30',
        max_pages=1,
        category_slugs=[],
        client_filter_keywords=[],
    )

    print(f"\nResults: {len(results)} jobs found")
    if results:
        r = results[0]
        print(f"  Title: {r.get('title', 'N/A')}")
        print(f"  Company: {r.get('company', 'N/A')}")
    return len(results) > 0


def test_irantalent():
    """Test IranTalent REST API crawler."""
    print("\n" + "="*60)
    print("TEST 4: IranTalent REST API Crawler")
    print("="*60)

    from core.crawlers.irantalent_crawler import crawl_irantalent

    results = crawl_irantalent(
        keywords='python',
        city='',
        level='all',
        time_range='30',
        max_pages=1,
        client_filter_keywords=[],
    )

    print(f"\nResults: {len(results)} jobs found")
    if results:
        r = results[0]
        print(f"  Title: {r.get('title', 'N/A')}")
        print(f"  Company: {r.get('company', 'N/A')}")
        print(f"  URL: {r.get('url', 'N/A')}")
    return len(results) > 0


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("#  CRAWLER TEST SUITE")
    print("#"*60)

    results = {}

    # Test Jobvision (most reliable)
    try:
        results['jobvision'] = test_jobvision()
    except Exception as e:
        print(f"Jobvision FAILED: {e}")
        results['jobvision'] = False

    try:
        results['jobvision_no_cat'] = test_jobvision_no_category()
    except Exception as e:
        print(f"Jobvision no-cat FAILED: {e}")
        results['jobvision_no_cat'] = False

    # Test E-estekhdam
    try:
        results['estekhdam'] = test_estekhdam()
    except Exception as e:
        print(f"E-estekhdam FAILED: {e}")
        results['estekhdam'] = False

    # Test IranTalent
    try:
        results['irantalent'] = test_irantalent()
    except Exception as e:
        print(f"IranTalent FAILED: {e}")
        results['irantalent'] = False

    # Summary
    print("\n" + "#"*60)
    print("#  SUMMARY")
    print("#"*60)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    if results.get('jobvision') or results.get('jobvision_no_cat'):
        print("\n  >> Jobvision API is working! The core search functionality is operational.")
    else:
        print("\n  >> WARNING: Jobvision API is not responding. Check your internet connection.")