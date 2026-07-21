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

# Markers that indicate a page requires JavaScript (SPA)
_JS_REQUIRED_MARKERS = [
    'جاوا اسکریپت غیرفعال',
    'noscript',
    'javascript is disabled',
    'requires javascript',
    'خطا در اتصال به سرور',
]


def _is_js_required_page(html: str) -> bool:
    """Check if the response is a JS-required SPA shell (not real content)."""
    html_lower = html.lower()
    for marker in _JS_REQUIRED_MARKERS:
        if marker in html_lower:
            return True
    # If the page is very small (< 15KB), it's likely a SPA shell or error
    if len(html) < 15000 and 'noscript' in html_lower:
        return True
    return False


def crawl_estekhdam(keywords: str, city: str = '', level: str = 'all',
                     time_range: str = '7', max_pages: int = 2) -> list:
    """
    Crawl e-estekhdam.com for job listings.
    Strategy: Quick BS4 probe -> if JS-required, go straight to Playwright.
    E-estekhdam is a full SPA — requests+BS4 will NOT find any job cards.
    """
    # Build search URL
    if city and city in CITY_MAP:
        search_path = f"/search/{CITY_MAP[city]}"
    elif keywords.strip():
        first_kw = keywords.strip().split()[0] if keywords.strip() else ''
        search_path = f"/search/{first_kw}"
    else:
        search_path = "/"

    level_keywords = LEVEL_KEYWORDS.get(level, [])

    # --- Phase 1: Quick probe with requests ---
    # E-estekhdam is a JavaScript SPA. We do a quick check to see if
    # the page returns real HTML content or a JS-required shell.
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        session.get(BASE_URL, timeout=8)
    except Exception:
        pass

    try:
        url = f"{BASE_URL}{search_path}"
        resp = session.get(url, headers=HEADERS, timeout=8)

        if resp.ok and not _is_js_required_page(resp.text):
            # Rare case: maybe they have SSR. Try to parse.
            logger.info("E-estekhdam: got real HTML content, trying BS4...")
            results = _parse_bs4(resp.text, seen_ids=set(), level_keywords=level_keywords,
                                 city=city, level=level)
            if results:
                return results
    except Exception as e:
        logger.debug(f"E-estekhdam probe error: {e}")

    # --- Phase 2: Playwright (required for this SPA) ---
    logger.info("E-estekhdam: site requires JavaScript, using Playwright...")
    return _crawl_with_playwright(keywords, city, level, time_range, max_pages, level_keywords, search_path)


def _parse_bs4(html: str, seen_ids: set, level_keywords: list,
               city: str = '', level: str = 'all') -> list:
    """Try to parse job items from HTML. Returns list or empty."""
    soup = BeautifulSoup(html, 'lxml')

    # Try multiple selector sets (most specific first)
    selector_sets = [
        '.job-list-item.item',
        '.job-listing',
        '[data-id]',
        '.card.job-card',
        '.job-card',
        '.vacancy-card',
        '.listing-card',
    ]

    job_items = []
    for sel in selector_sets:
        job_items = soup.select(sel)
        if job_items:
            break

    if not job_items:
        return []

    results = []
    for item in job_items:
        job_id = item.get('data-id', '') or item.get('id', '')
        if job_id in seen_ids:
            continue
        seen_ids.add(job_id)

        title_el = item.select_one('.title span, .job-title, h2 a, h3 a, .title a')
        title = title_el.get_text(strip=True) if title_el else ''
        if not title:
            link_el = item.select_one('a[href]')
            if link_el:
                title = link_el.get('title', '') or link_el.get_text(strip=True)

        company_el = item.select_one('.subtitle span, .company-name, .company')
        company = company_el.get_text(strip=True) if company_el else ''

        city_el = item.select_one('.provinces .label, .location, .city')
        city_name = city_el.get_text(strip=True) if city_el else (city or '')

        link_el = item.select_one('a[href]')
        href = link_el.get('href', '') if link_el else ''
        if href and not href.startswith('http'):
            href = f"{BASE_URL}{href}"

        if level != 'all' and level_keywords:
            item_text = item.get_text()
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

    return results


def _crawl_with_playwright(keywords, city, level, time_range, max_pages,
                           level_keywords, search_path):
    """Crawl using Playwright with system Chrome for JS-rendered pages."""
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
                "E-estekhdam: No browser available. "
                "Install Google Chrome or Edge to crawl this platform."
            )
            return []

        page = bc.context.new_page()

        # Navigate to search page
        url = f"{BASE_URL}{search_path}"
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=25000)
            # Wait for JS to render job cards
            page.wait_for_timeout(4000)
        except Exception as e:
            logger.error(f"E-estekhdam Playwright navigation failed: {e}")
            return []

        results = []
        seen_ids = set()

        # Multiple selector sets for robustness
        selector_sets = [
            '.job-list-item.item',
            '[data-id]',
            '.job-listing',
            '.card.job-card',
            '.job-card',
            '.vacancy-card',
            '.listing-card',
            'a[href*="/job/"]',
            'a[href*="/استخدام-"]',
        ]

        for pg in range(max_pages):
            try:
                # Try each selector set until we find items
                items = []
                for sel in selector_sets:
                    items = page.query_selector_all(sel)
                    if items:
                        logger.info(f"E-estekhdam (PW): found items with selector '{sel}'")
                        break

                if not items:
                    logger.info(f"E-estekhdam (PW): no items on page {pg + 1}")
                    break

                for item in items:
                    jid = item.get_attribute('data-id') or item.get_attribute('id') or ''
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    # Try multiple title selectors
                    title = ''
                    for sel in ['.title span', '.job-title', 'h2 a', 'h3 a', 'a']:
                        title_el = item.query_selector(sel)
                        if title_el:
                            title = title_el.inner_text().strip()
                            if title:
                                break
                    if not title:
                        continue

                    company = ''
                    for sel in ['.subtitle span', '.company-name', '.company']:
                        company_el = item.query_selector(sel)
                        if company_el:
                            company = company_el.inner_text().strip()
                            break

                    city_name = city or ''
                    for sel in ['.provinces .label', '.location', '.city']:
                        city_el = item.query_selector(sel)
                        if city_el:
                            city_name = city_el.inner_text().strip()
                            break

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

                logger.info(f"E-estekhdam (PW) page {pg + 1}: {len(results)} total items")

                # Try to go to next page
                next_btn = page.query_selector(
                    'a.next, [rel="next"], .pagination .next, '
                    'button.next, [aria-label="Next"], .pagination-next, '
                    'a[aria-label="next"], li.next a'
                )
                if next_btn and next_btn.is_visible():
                    next_btn.click()
                    page.wait_for_timeout(3000)
                else:
                    break

            except Exception as e:
                logger.error(f"E-estekhdam PW page error: {e}")
                break

        return results

    finally:
        bc.__exit__(None, None, None)