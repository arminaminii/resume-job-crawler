import requests
import re
import time
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.e-estekhdam.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

CITY_MAP = {
    'تهران': 'استخدام-در-تهران',
    'اصفهان': 'استخدام-در-اصفهان',
    'البرز': 'استخدام-در-البرز',
    'خراسان رضوی': 'استخدام-در-خراسان-رضوی',
    'فارس': 'استخدام-در-فارس',
    'خوزستان': 'استخدام-در-خوزستان',
    'گیلان': 'استخدام-در-گیلان',
    'مازندران': 'استخدام-در-مازندران',
    'آذربایجان شرقی': 'استخدام-در-آذربایجان-شرقی',
    'آذربایجان غربی': 'استخدام-در-آذربایجان-غربی',
    'کرمان': 'استخدام-در-کرمان',
    'هرمزگان': 'استخدام-در-هرمزگان',
    'یزد': 'استخدام-در-یزد',
    'مرکزی': 'استخدام-در-مرکزی',
    'گلستان': 'استخدام-در-گلستان',
    'سمنان': 'استخدام-در-سمنان',
    'کرمانشاه': 'استخدام-در-کرمانشاه',
    'همدان': 'استخدام-در-همدان',
    'لرستان': 'استخدام-در-لرستان',
    'بوشهر': 'استخدام-در-بوشهر',
    'زنجان': 'استخدام-در-زنجان',
    'اردبیل': 'استخدام-در-اردبیل',
}

LEVEL_KEYWORDS = {
    'junior': ['کارآموز', 'جونیور', 'مبتدی', 'مقدماتی'],
    'mid': ['متوسط', 'میان‌رده', 'Mid-level'],
    'senior': ['ارشد', 'سنیور', 'Senior', 'بالا'],
    'manager': ['مدیر', 'Manager', 'رهبر', 'سرپرست'],
}


def crawl_estekhdam(keywords: str, city: str = '', level: str = 'all',
                     time_range: str = '7', max_pages: int = 3) -> list:
    """
    Crawl e-estekhdam.com for job listings.
    Tries homepage SSR first, falls back to Playwright if needed.
    """
    results = []
    seen_ids = set()

    # Build search URL
    if city and city in CITY_MAP:
        search_path = f"/search/{CITY_MAP[city]}"
    elif keywords.strip():
        search_path = f"/search/{keywords.strip()}"
    else:
        search_path = "/"

    # Level filter keywords
    level_keywords = LEVEL_KEYWORDS.get(level, [])

    for page in range(1, max_pages + 1):
        try:
            url = f"{BASE_URL}{search_path}" if page == 1 else f"{BASE_URL}{search_path}?page={page}"
            resp = requests.get(url, headers=HEADERS, timeout=30)

            if resp.status_code == 403:
                logger.warning("E-estekhdam returned 403, trying Playwright fallback...")
                return _crawl_with_playwright(
                    keywords, city, level, time_range, max_pages
                )

            if not resp.ok:
                continue

            soup = BeautifulSoup(resp.text, 'lxml')
            job_items = soup.select('.job-list-item.item')

            if not job_items:
                # Try alternative selectors
                job_items = soup.select('[data-id]')
                if not job_items:
                    break

            for item in job_items:
                job_id = item.get('data-id', '')
                if not job_id:
                    continue
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                # Extract title
                title_el = item.select_one('.title span')
                title = title_el.get_text(strip=True) if title_el else ''

                # Extract company
                company_el = item.select_one('.subtitle span')
                company = company_el.get_text(strip=True) if company_el else ''

                # Extract city/province
                provinces = item.select('.provinces .label')
                cities = [p.get_text(strip=True) for p in provinces]
                city_name = cities[0] if cities else (city or '')

                # Extract link
                link_el = item.select_one('a[href]')
                href = link_el.get('href', '') if link_el else ''
                if href and not href.startswith('http'):
                    href = f"{BASE_URL}{href}"

                # Level filtering
                if level != 'all' and level_keywords:
                    item_text = item.get_text()
                    if not any(kw in item_text for kw in level_keywords):
                        continue

                results.append({
                    'platform': 'e_estekhdam',
                    'title': title,
                    'company': company,
                    'city': city_name,
                    'province': city_name,
                    'salary': '',
                    'job_type': '',
                    'seniority_level': level if level != 'all' else '',
                    'description': '',
                    'skills': [],
                    'url': href,
                    'remote': False,
                    'posted_date': '',
                })

            logger.info(f"E-estekhdam page {page}: got {len(job_items)} items")
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"E-estekhdam crawl error: {e}")
            break

    return results


def _crawl_with_playwright(keywords, city, level, time_range, max_pages):
    """Fallback: use Playwright for JavaScript-rendered pages."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not available for e-estekhdam fallback")
        return []

    results = []
    seen_ids = set()
    level_keywords = LEVEL_KEYWORDS.get(level, [])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            locale='fa-IR',
        )
        page = context.new_page()

        if city and city in CITY_MAP:
            url = f"{BASE_URL}/search/{CITY_MAP[city]}"
        elif keywords.strip():
            url = f"{BASE_URL}/search/{keywords.strip()}"
        else:
            url = BASE_URL

        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
        except Exception as e:
            logger.error(f"Playwright navigation failed: {e}")
            browser.close()
            return []

        for pg in range(max_pages):
            try:
                items = page.query_selector_all('.job-list-item.item, [data-id]')
                if not items:
                    break

                for item in items:
                    jid = item.get_attribute('data-id') or ''
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    title_el = item.query_selector('.title span')
                    title = title_el.inner_text().strip() if title_el else ''

                    company_el = item.query_selector('.subtitle span')
                    company = company_el.inner_text().strip() if company_el else ''

                    prov_els = item.query_selector_all('.provinces .label')
                    cities = [el.inner_text().strip() for el in prov_els]
                    city_name = cities[0] if cities else (city or '')

                    link_el = item.query_selector('a[href]')
                    href = link_el.get_attribute('href') or '' if link_el else ''
                    if href and not href.startswith('http'):
                        href = f"{BASE_URL}{href}"

                    if level != 'all' and level_keywords:
                        item_text = item.inner_text()
                        if not any(kw in item_text for kw in level_keywords):
                            continue

                    results.append({
                        'platform': 'e_estekhdam',
                        'title': title,
                        'company': company,
                        'city': city_name,
                        'province': city_name,
                        'salary': '',
                        'job_type': '',
                        'seniority_level': level if level != 'all' else '',
                        'description': '',
                        'skills': [],
                        'url': href,
                        'remote': False,
                        'posted_date': '',
                    })

                # Try pagination
                next_btn = page.query_selector('a.next, [rel="next"], .pagination .next')
                if next_btn:
                    next_btn.click()
                    page.wait_for_timeout(2000)
                else:
                    break

            except Exception as e:
                logger.error(f"Playwright page error: {e}")
                break

        browser.close()

    return results