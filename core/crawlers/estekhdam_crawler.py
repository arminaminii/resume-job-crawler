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
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
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
                     time_range: str = '7', max_pages: int = 2) -> list:
    """
    Crawl e-estekhdam.com for job listings.
    Strategy: Try requests+BS4 first, fall back to Playwright with system Chrome.
    """
    results = []
    seen_ids = set()

    # Build search URL
    if city and city in CITY_MAP:
        search_path = f"/search/{CITY_MAP[city]}"
    elif keywords.strip():
        # Only use first keyword for cleaner URL
        first_kw = keywords.strip().split()[0] if keywords.strip() else ''
        search_path = f"/search/{first_kw}"
    else:
        search_path = "/"

    level_keywords = LEVEL_KEYWORDS.get(level, [])

    # --- Phase 1: Try requests + BeautifulSoup ---
    session = requests.Session()
    session.headers.update(HEADERS)

    # First visit homepage to get cookies
    try:
        session.get(BASE_URL, timeout=10)
    except Exception:
        pass

    bs4_worked = False
    for page in range(1, max_pages + 1):
        try:
            url = f"{BASE_URL}{search_path}" if page == 1 else f"{BASE_URL}{search_path}?page={page}"
            resp = session.get(url, headers=HEADERS, timeout=10)

            if resp.status_code == 403:
                logger.warning("E-estekhdam: 403 from requests, switching to Playwright...")
                break

            if not resp.ok:
                logger.warning(f"E-estekhdam: HTTP {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, 'lxml')

            # Try multiple selectors for job items
            job_items = (
                soup.select('.job-list-item.item') or
                soup.select('.job-listing') or
                soup.select('[data-id]') or
                soup.select('.card.job-card')
            )

            if not job_items:
                logger.info("E-estekhdam (BS4): no items found, trying Playwright...")
                break

            bs4_worked = True
            for item in job_items:
                job_id = item.get('data-id', '') or item.get('id', '')
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                # Extract title
                title_el = item.select_one('.title span, .job-title, h2 a, h3 a, .title a')
                title = title_el.get_text(strip=True) if title_el else ''
                if not title:
                    link_el = item.select_one('a[href]')
                    if link_el:
                        title = link_el.get('title', '') or link_el.get_text(strip=True)

                # Extract company
                company_el = item.select_one('.subtitle span, .company-name, .company')
                company = company_el.get_text(strip=True) if company_el else ''

                # Extract city/province
                city_el = item.select_one('.provinces .label, .location, .city')
                city_name = city_el.get_text(strip=True) if city_el else (city or '')

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

                if title:  # Only add if we found a title
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

            logger.info(f"E-estekhdam (BS4) page {page}: got {len(results)} total items")
            time.sleep(1)

        except requests.Timeout:
            logger.error("E-estekhdam: request timeout")
            break
        except Exception as e:
            logger.error(f"E-estekhdam (BS4) error: {e}")
            break

    if bs4_worked and results:
        return results

    # --- Phase 2: Playwright with system Chrome ---
    logger.info("E-estekhdam: trying Playwright with system Chrome...")
    return _crawl_with_playwright(keywords, city, level, time_range, max_pages, level_keywords)


def _crawl_with_playwright(keywords, city, level, time_range, max_pages, level_keywords):
    """Fallback: use Playwright with system Chrome for JS-rendered pages."""
    from .playwright_helper import BrowserContext

    bc = BrowserContext(
        headless=True,
        user_agent=HEADERS["User-Agent"],
        locale='fa-IR',
    )

    try:
        bc.__enter__()
        if not bc.is_available:
            logger.warning(
                "E-estekhdam: No browser available. Install Google Chrome or Edge."
            )
            return []

        page = bc.context.new_page()

        if city and city in CITY_MAP:
            url = f"{BASE_URL}/search/{CITY_MAP[city]}"
        elif keywords.strip():
            first_kw = keywords.strip().split()[0]
            url = f"{BASE_URL}/search/{first_kw}"
        else:
            url = BASE_URL

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(2000)
        except Exception as e:
            logger.error(f"E-estekhdam Playwright navigation failed: {e}")
            return []

        results = []
        seen_ids = set()

        for pg in range(max_pages):
            try:
                items = page.query_selector_all(
                    '.job-list-item.item, [data-id], .job-listing, .card.job-card'
                )
                if not items:
                    logger.info(f"E-estekhdam (PW): no items on page {pg + 1}")
                    break

                for item in items:
                    jid = item.get_attribute('data-id') or item.get_attribute('id') or ''
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    title_el = item.query_selector('.title span, .job-title, h2 a, h3 a')
                    title = title_el.inner_text().strip() if title_el else ''
                    if not title:
                        link_el = item.query_selector('a[href]')
                        if link_el:
                            title = (link_el.get_attribute('title') or
                                     link_el.inner_text().strip())

                    company_el = item.query_selector('.subtitle span, .company-name, .company')
                    company = company_el.inner_text().strip() if company_el else ''

                    city_el = item.query_selector('.provinces .label, .location, .city')
                    city_name = city_el.inner_text().strip() if city_el else (city or '')

                    link_el = item.query_selector('a[href]')
                    href = link_el.get_attribute('href') or '' if link_el else ''
                    if href and not href.startswith('http'):
                        href = f"{BASE_URL}{href}"

                    if level != 'all' and level_keywords:
                        item_text = item.inner_text()
                        if not any(kw in item_text for kw in level_keywords):
                            continue

                    if title:
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

                logger.info(f"E-estekhdam (PW) page {pg + 1}: {len(results)} total items")

                next_btn = page.query_selector('a.next, [rel="next"], .pagination .next')
                if next_btn:
                    next_btn.click()
                    page.wait_for_timeout(2000)
                else:
                    break

            except Exception as e:
                logger.error(f"E-estekhdam PW page error: {e}")
                break

        return results

    finally:
        bc.__exit__(None, None, None)