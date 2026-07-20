import logging
import time

logger = logging.getLogger(__name__)

BASE_URL = "https://www.irantalent.com"

CITY_SLUGS = {
    'تهران': 'jobs-in-tehran',
    'اصفهان': 'jobs-in-isfahan',
    'البرز': 'jobs-in-alborz',
    'خراسان رضوی': 'jobs-in-khorasan-razavi',
    'فارس': 'jobs-in-fars',
    'خوزستان': 'jobs-in-khoozestan',
    'گیلان': 'jobs-in-gilan',
    'مازندران': 'jobs-in-mazandaran',
    'آذربایجان شرقی': 'jobs-in-east-azarbaijan',
    'آذربایجان غربی': 'jobs-in-west-azarbaijan',
    'کرمان': 'jobs-in-kerman',
    'هرمزگان': 'jobs-in-hormozgan',
    'یزد': 'jobs-in-yazd',
    'مرکزی': 'jobs-in-markazi',
    'گلستان': 'jobs-in-golestan',
    'کرمانشاه': 'jobs-in-kermanshah',
    'همدان': 'jobs-in-hamedan',
    'بوشهر': 'jobs-in-bushehr',
}

SENIORITY_SLUGS = {
    'junior': 'jobs-for-junior-professional',
    'mid': 'jobs-for-mid-level-professional',
    'senior': 'jobs-for-experienced-professional',
    'manager': 'jobs-for-manager',
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
}


def _check_playwright_available():
    """Check if Playwright + Chromium browser are available."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                return True
            except Exception:
                return False
    except ImportError:
        return False


def crawl_irantalent(keywords: str, city: str = '', level: str = 'all',
                       time_range: str = '7', max_pages: int = 3) -> list:
    """
    Crawl IranTalent using Playwright (Angular SPA).
    Returns empty list with warning if Playwright is not available.
    """
    if not _check_playwright_available():
        logger.warning(
            "IranTalent: Playwright/Chromium not available. "
            "Cannot crawl this platform (Angular SPA). "
            "Install Playwright browsers: set PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH "
            "env var or run 'playwright install chromium' with VPN."
        )
        return []

    results = []
    seen_urls = set()

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                locale='en-US',
            )
            page = context.new_page()

            # Build URL - use English routes for easier parsing
            url_parts = [f"{BASE_URL}/en/jobs"]

            if city and city in CITY_SLUGS:
                url_parts.append(CITY_SLUGS[city])
            elif level and level in SENIORITY_SLUGS:
                url_parts.append(SENIORITY_SLUGS[level])

            url = '/'.join(url_parts)

            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(3000)
            except Exception as e:
                logger.error(f"IranTalent navigation failed: {e}")
                browser.close()
                return []

            for pg in range(max_pages):
                try:
                    # Wait for job cards to render (Angular)
                    page.wait_for_selector('.job, .job-card, [class*="job"]', timeout=10000)

                    # Try to intercept API calls for cleaner data
                    job_cards = page.query_selector_all('.job, .job-card, article')

                    if not job_cards:
                        # Try broader selectors
                        job_cards = page.query_selector_all('a[href*="/job"], a[href*="/position"]')

                    if not job_cards:
                        logger.info(f"IranTalent: no job cards found on page {pg + 1}")
                        break

                    for card in job_cards:
                        try:
                            card_text = card.inner_text()
                            if len(card_text.strip()) < 10:
                                continue

                            link_el = card.query_selector('a[href]') or (card if card.evaluate('el => el.tagName') == 'A' else None)
                            if not link_el:
                                continue

                            href = link_el.get_attribute('href') or ''
                            if not href or href in seen_urls:
                                continue
                            seen_urls.add(href)

                            if not href.startswith('http'):
                                href = f"{BASE_URL}{href}"

                            # Extract title
                            title = ''
                            title_el = card.query_selector('h2, h3, .job-title, [class*="title"]')
                            if title_el:
                                title = title_el.inner_text().strip()
                            if not title:
                                title = link_el.inner_text().strip()[:100]

                            # Extract company
                            company = ''
                            company_el = card.query_selector('[class*="company"], [class*="employer"]')
                            if company_el:
                                company = company_el.inner_text().strip()

                            # Extract location
                            city_name = city or ''
                            loc_el = card.query_selector('[class*="location"], [class*="city"]')
                            if loc_el:
                                city_name = loc_el.inner_text().strip()

                            # Extract level
                            sen_level = ''
                            level_el = card.query_selector('[class*="seniority"], [class*="level"]')
                            if level_el:
                                sen_level = level_el.inner_text().strip()

                            # Extract remote
                            remote = 'remote' in card_text.lower() or 'دورکار' in card_text

                            # Filter by keywords if provided
                            if keywords.strip():
                                kw = keywords.strip().lower()
                                if kw not in card_text.lower() and kw not in title.lower():
                                    continue

                            results.append({
                                'platform': 'irantalent',
                                'title': title,
                                'company': company,
                                'city': city_name,
                                'province': city_name,
                                'salary': '',
                                'job_type': '',
                                'seniority_level': sen_level,
                                'description': card_text[:500],
                                'skills': [],
                                'url': href,
                                'remote': remote,
                                'posted_date': '',
                            })

                        except Exception as e:
                            logger.debug(f"IranTalent card parse error: {e}")
                            continue

                    logger.info(f"IranTalent page {pg + 1}: got {len(job_cards)} cards")

                    # Pagination
                    next_btn = page.query_selector(
                        'a.next, button.next, [aria-label="Next"], .pagination-next'
                    )
                    if next_btn and next_btn.is_visible():
                        next_btn.click()
                        page.wait_for_timeout(3000)
                    else:
                        break

                except Exception as e:
                    logger.error(f"IranTalent page {pg + 1} error: {e}")
                    break

            browser.close()

    except Exception as e:
        logger.error(f"IranTalent Playwright error: {e}")

    return results