import logging
import time
import json
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.irantalent.com"
API_BASE = "https://www.irantalent.com/api"

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

# Single API endpoint to try (the most likely one)
_API_ENDPOINTS = [
    f'{API_BASE}/job/search',
]

def crawl_irantalent(keywords: str, city: str = '', level: str = 'all',
                       time_range: str = '7', max_pages: int = 2) -> list:
    """
    Crawl IranTalent.
    Strategy:
      1. Try API calls (requests) - fastest and most reliable
      2. Fall back to Playwright with system Chrome if API fails
    """
    results = []

    # --- Phase 1: Try API (requests) ---
    api_results = _crawl_via_api(keywords, city, level, time_range, max_pages)
    if api_results:
        return api_results

    # --- Phase 2: Playwright with system Chrome ---
    logger.info("IranTalent: API not available, trying Playwright with system Chrome...")
    return _crawl_via_playwright(keywords, city, level, time_range, max_pages)


def _crawl_via_api(keywords, city, level, time_range, max_pages):
    """Try to crawl IranTalent via their internal API."""
    results = []
    session = requests.Session()
    session.headers.update(HEADERS)

    # Try each API endpoint until one works
    working_endpoint = None
    for endpoint in _API_ENDPOINTS:
        try:
            payload = {
                'keyword': (keywords.strip() if keywords else ''),
                'location': CITY_SLUGS.get(city, '') if city else '',
                'seniority': SENIORITY_SLUGS.get(level, '') if level != 'all' else '',
                'page': 1,
                'limit': 20,
            }
            resp = session.post(
                endpoint,
                json=payload,
                timeout=10,
                headers={**HEADERS, 'Content-Type': 'application/json'},
            )
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if data and (data.get('data') or data.get('items') or data.get('jobs') or data.get('results')):
                        working_endpoint = endpoint
                        logger.info(f"IranTalent: Working API endpoint found: {endpoint}")
                        break
                except (json.JSONDecodeError, ValueError):
                    continue
            elif resp.status_code == 403:
                logger.warning(f"IranTalent API {endpoint}: 403 forbidden")
                break
        except (requests.Timeout, requests.ConnectionError) as e:
            logger.debug(f"IranTalent API connection issue: {e}")
            continue
        except Exception as e:
            logger.debug(f"IranTalent API error: {e}")
            continue

    if not working_endpoint:
        logger.info("IranTalent: No working API endpoint found")
        return []

    # Now crawl pages using the working endpoint
    for page in range(1, max_pages + 1):
        try:
            payload = {
                'keyword': (keywords.strip() if keywords else ''),
                'location': CITY_SLUGS.get(city, '') if city else '',
                'seniority': SENIORITY_SLUGS.get(level, '') if level != 'all' else '',
                'page': page,
                'limit': 20,
            }
            resp = session.post(
                working_endpoint,
                json=payload,
                timeout=10,
                headers={**HEADERS, 'Content-Type': 'application/json'},
            )

            if not resp.ok:
                break

            data = resp.json()
            jobs = (
                data.get('data', {}).get('items', []) or
                data.get('data', {}).get('jobs', []) or
                data.get('items', []) or
                data.get('jobs', []) or
                data.get('results', []) or
                (data.get('data', []) if isinstance(data.get('data'), list) else [])
            )

            if not jobs:
                break

            for job in jobs:
                if not isinstance(job, dict):
                    continue

                title = (job.get('title', '') or job.get('jobTitle', '') or job.get('name', '') or '')

                company_info = job.get('company', {}) or {}
                if isinstance(company_info, dict):
                    company = company_info.get('name', '') or company_info.get('title', '') or ''
                else:
                    company = str(company_info)

                loc_info = job.get('location', {}) or {}
                if isinstance(loc_info, dict):
                    city_name = loc_info.get('city', '') or loc_info.get('name', '') or (city or '')
                else:
                    city_name = str(loc_info) if loc_info else (city or '')

                salary = ''
                salary_info = job.get('salary', {})
                if isinstance(salary_info, dict):
                    min_s = salary_info.get('min', '')
                    max_s = salary_info.get('max', '')
                    if min_s or max_s:
                        salary = f"{min_s} - {max_s}"

                seniority = (job.get('seniorityLevel', '') or job.get('seniority', '') or
                             job.get('level', '') or '')
                if isinstance(seniority, dict):
                    seniority = seniority.get('title', '') or seniority.get('name', '')

                skills = job.get('skills', [])
                if isinstance(skills, list):
                    skills = [s.get('name', s) if isinstance(s, dict) else s for s in skills]
                else:
                    skills = []

                desc = job.get('description', '') or ''
                job_id = job.get('id', '') or job.get('slug', '')
                url = f"{BASE_URL}/jobs/{job_id}" if job_id else ''
                remote = job.get('isRemote', False) or job.get('remote', False)

                results.append({
                    'platform': 'irantalent',
                    'title': title,
                    'company': company,
                    'city': city_name,
                    'province': city_name,
                    'salary': salary,
                    'job_type': job.get('jobType', '') or job.get('employmentType', ''),
                    'seniority_level': seniority,
                    'description': desc[:500] if desc else '',
                    'skills': skills,
                    'url': url,
                    'remote': remote,
                    'posted_date': job.get('createdAt', '') or '',
                })

            logger.info(f"IranTalent (API) page {page}: got {len(jobs)} jobs")
            time.sleep(0.8)

        except requests.Timeout:
            logger.warning(f"IranTalent API timeout at page {page}")
            break
        except Exception as e:
            logger.error(f"IranTalent API page {page} error: {e}")
            break

    if results:
        logger.info(f"IranTalent (API) total: {len(results)} jobs")
    return results


def _crawl_via_playwright(keywords, city, level, time_range, max_pages):
    """Fallback: use Playwright with system Chrome for Angular SPA."""
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

        # Build URL
        url_parts = [f"{BASE_URL}/en/jobs"]
        if city and city in CITY_SLUGS:
            url_parts.append(CITY_SLUGS[city])
        elif level and level in SENIORITY_SLUGS:
            url_parts.append(SENIORITY_SLUGS[level])
        url = '/'.join(url_parts)

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(3000)
        except Exception as e:
            logger.error(f"IranTalent PW navigation failed: {e}")
            return []

        results = []
        seen_urls = set()

        for pg in range(max_pages):
            try:
                try:
                    page.wait_for_selector('a[href*="/job"], .job-card, article', timeout=6000)
                except Exception:
                    pass

                job_cards = (
                    page.query_selector_all('.job-card, article') or
                    page.query_selector_all('a[href*="/job"], a[href*="/position"]')
                )

                if not job_cards:
                    logger.info(f"IranTalent (PW): no cards on page {pg + 1}")
                    break

                for card in job_cards:
                    try:
                        card_text = card.inner_text()
                        if len(card_text.strip()) < 10:
                            continue

                        link_el = card.query_selector('a[href]') or (
                            card if card.evaluate('el => el.tagName') == 'A' else None
                        )
                        if not link_el:
                            continue

                        href = link_el.get_attribute('href') or ''
                        if not href or href in seen_urls:
                            continue
                        seen_urls.add(href)

                        if not href.startswith('http'):
                            href = f"{BASE_URL}{href}"

                        title_el = card.query_selector('h2, h3, .job-title, [class*="title"]')
                        title = title_el.inner_text().strip() if title_el else ''
                        if not title:
                            title = link_el.inner_text().strip()[:100]

                        company_el = card.query_selector('[class*="company"], [class*="employer"]')
                        company = company_el.inner_text().strip() if company_el else ''

                        city_name = city or ''
                        loc_el = card.query_selector('[class*="location"], [class*="city"]')
                        if loc_el:
                            city_name = loc_el.inner_text().strip()

                        sen_level = ''
                        level_el = card.query_selector('[class*="seniority"], [class*="level"]')
                        if level_el:
                            sen_level = level_el.inner_text().strip()

                        remote = 'remote' in card_text.lower() or 'دورکار' in card_text

                        if title:
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

                next_btn = page.query_selector('a.next, button.next, [aria-label="Next"], .pagination-next')
                if next_btn and next_btn.is_visible():
                    next_btn.click()
                    page.wait_for_timeout(2000)
                else:
                    break

            except Exception as e:
                logger.error(f"IranTalent PW page {pg + 1} error: {e}")
                break

        return results

    finally:
        bc.__exit__(None, None, None)
