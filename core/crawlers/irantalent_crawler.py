import logging
import time
import json
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.irantalent.com"
# IranTalent uses api.irantalent.com for their backend API,
# but the job search API is NOT publicly accessible (requires auth/cookies).
# The site is a full Angular SPA — only Playwright can crawl it.

CITY_SLUGS = {
    'تهران': 'tehran',
    'اصفهان': 'isfahan',
    'البرز': 'alborz',
    'خراسان رضوی': 'khorasan-razavi',
    'فارس': 'fars',
    'خوزستان': 'khouzestan',
    'گیلان': 'gilan',
    'مازندران': 'mazandaran',
    'آذربایجان شرقی': 'east-azarbaijan',
    'آذربایجان غربی': 'west-azarbaijan',
    'کرمان': 'kerman',
    'هرمزگان': 'hormozgan',
    'یزد': 'yazd',
    'مرکزی': 'markazi',
    'گلستان': 'golestan',
    'کرمانشاه': 'kermanshah',
    'همدان': 'hamedan',
    'بوشهر': 'bushehr',
}

SENIORITY_SLUGS = {
    'junior': 'Junior',
    'mid': 'Mid-Level',
    'senior': 'Senior',
    'manager': 'Manager',
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
    "Referer": "https://www.irantalent.com/",
    "Origin": "https://www.irantalent.com",
}


def crawl_irantalent(keywords: str, city: str = '', level: str = 'all',
                       time_range: str = '7', max_pages: int = 2) -> list:
    """
    Crawl IranTalent.
    IranTalent is a full Angular SPA with NO public REST API for job search.
    Strategy: Go directly to Playwright with system Chrome.
    """
    logger.info("IranTalent: SPA site with no public API, using Playwright...")
    return _crawl_via_playwright(keywords, city, level, time_range, max_pages)


def _crawl_via_playwright(keywords, city, level, time_range, max_pages):
    """Crawl IranTalent using Playwright with system Chrome for Angular SPA."""
    from .playwright_helper import BrowserContext

    bc = BrowserContext(
        headless=True,
        user_agent=HEADERS["User-Agent"],
        locale='en-US',
    )

    try:
        bc.__enter__()
        if not bc.is_available:
            logger.warning(
                "IranTalent: No browser available. "
                "Install Google Chrome/Edge, or run 'playwright install chromium' with VPN."
            )
            return []

        page = bc.context.new_page()

        # Build URL based on IranTalent's URL structure:
        # /jobs/search?keyword=... or /jobs/city-slug or /en/jobs
        url_parts = [f"{BASE_URL}/jobs"]
        if keywords and keywords.strip():
            url_parts.append(f"search?keyword={keywords.strip().split()[0]}")
        elif city and city in CITY_SLUGS:
            url_parts.append(f"in-{CITY_SLUGS[city]}")
        url = '/'.join(url_parts)

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=25000)
            # Angular needs time to render
            page.wait_for_timeout(5000)
        except Exception as e:
            logger.error(f"IranTalent PW navigation failed: {e}")
            return []

        results = []
        seen_urls = set()

        # Multiple selector sets for robustness
        selector_sets = [
            'a[href*="/jobs/"]',
            '.job-card, article',
            '[class*="job-card"]',
            '[class*="position-card"]',
            'a[href*="/position/"]',
        ]

        for pg in range(max_pages):
            try:
                # Wait for content to appear
                try:
                    page.wait_for_selector(
                        'a[href*="/jobs/"], .job-card, article, [class*="position"]',
                        timeout=8000
                    )
                except Exception:
                    # If no selector matches, the page might not have loaded
                    logger.info(f"IranTalent (PW): no job selectors found on page {pg + 1}")
                    # Take screenshot for debugging
                    try:
                        content = page.inner_text('body')
                        if len(content.strip()) < 50:
                            logger.warning(f"IranTalent (PW): page body is empty")
                            break
                    except Exception:
                        pass

                # Try each selector set
                job_cards = []
                for sel in selector_sets:
                    job_cards = page.query_selector_all(sel)
                    if job_cards:
                        logger.info(f"IranTalent (PW): found items with selector '{sel}'")
                        break

                if not job_cards:
                    logger.info(f"IranTalent (PW): no cards on page {pg + 1}")
                    break

                for card in job_cards:
                    try:
                        card_text = card.inner_text()
                        if len(card_text.strip()) < 10:
                            continue

                        # Get the link/href
                        link_el = card.query_selector('a[href]') if 'a' not in (
                            card.evaluate('el => el.tagName') if card else ''
                        ) else None
                        if not link_el:
                            tag_name = card.evaluate('el => el.tagName')
                            if tag_name == 'A':
                                link_el = card
                            else:
                                link_el = card.query_selector('a[href]')

                        if not link_el:
                            continue

                        href = link_el.get_attribute('href') or ''
                        if not href or href in seen_urls:
                            continue

                        # Skip navigation links, non-job links
                        if any(skip in href for skip in ['/login', '/register', '/employer',
                                                           '/candidate', '/about', '/contact',
                                                           '/blog', '/pricing', '/fa/', '/en/']):
                            continue

                        seen_urls.add(href)

                        if not href.startswith('http'):
                            href = f"{BASE_URL}{href}"

                        # Extract title
                        title = ''
                        for sel in ['h2', 'h3', '.job-title', '[class*="title"]', '[class*="position-title"]']:
                            title_el = card.query_selector(sel)
                            if title_el:
                                title = title_el.inner_text().strip()
                                if title:
                                    break
                        if not title:
                            title = link_el.inner_text().strip()[:100]
                        if not title:
                            continue

                        # Extract company
                        company = ''
                        for sel in ['[class*="company"]', '[class*="employer"]', '[class*="org"]']:
                            company_el = card.query_selector(sel)
                            if company_el:
                                company = company_el.inner_text().strip()
                                if company:
                                    break

                        # Extract city/location
                        city_name = city or ''
                        for sel in ['[class*="location"]', '[class*="city"]', '[class*="province"]']:
                            loc_el = card.query_selector(sel)
                            if loc_el:
                                city_name = loc_el.inner_text().strip()
                                if city_name:
                                    break

                        # Extract seniority level
                        sen_level = ''
                        for sel in ['[class*="seniority"]', '[class*="level"]', '[class*="experience"]']:
                            level_el = card.query_selector(sel)
                            if level_el:
                                sen_level = level_el.inner_text().strip()
                                if sen_level:
                                    break

                        remote = 'remote' in card_text.lower() or 'دورکار' in card_text

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

                logger.info(f"IranTalent (PW) page {pg + 1}: {len(results)} total")

                # Try pagination
                next_btn = page.query_selector(
                    'a.next, button.next, [aria-label="Next"], '
                    '.pagination-next, a[aria-label="next"], '
                    'li.next a, [class*="pagination"] [class*="next"]'
                )
                if next_btn and next_btn.is_visible():
                    next_btn.click()
                    page.wait_for_timeout(3000)
                else:
                    break

            except Exception as e:
                logger.error(f"IranTalent PW page {pg + 1} error: {e}")
                break

        return results

    finally:
        bc.__exit__(None, None, None)