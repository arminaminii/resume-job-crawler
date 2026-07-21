"""
IranTalent crawler — uses Playwright with system Chrome.

IranTalent (irantalent.com) is an Angular SPA with NO public job search API.
The only public API endpoint is /api/v1/public-area/home-page (homepage data).
Job search requires client-side rendering via Angular.

Strategy:
1. Navigate to /en/jobs (English has more structured data)
2. Wait for Angular to render job cards
3. Extract data from rendered DOM
4. Handle pagination via clicking "Load more" or next page

HTML Structure (Angular SPA, rendered client-side):
- Job cards are inside elements with links to /en/job/{slug}/{id}
- Each card contains: title, company, location, seniority, job type, skills
- URL pattern: /en/job/{position-slug}/{numeric-id}
"""
import logging
import time

logger = logging.getLogger(__name__)

BASE_URL = "https://www.irantalent.com"
JOBS_URL = f"{BASE_URL}/en/jobs"

# City slug mapping for URL-based filtering
CITY_SLUGS = {
    'تهران': 'tehran',
    'اصفهان': 'isfahan',
    'البرز': 'alborz',
    'خراسان رضوی': 'mashhad',
    'فارس': 'shiraz',
    'خوزستان': 'ahvaz',
    'گیلان': 'rasht',
    'مازندران': 'sari',
    'آذربایجان شرقی': 'tabriz',
    'آذربایجان غربی': 'urmia',
    'کرمان': 'kerman',
    'هرمزگان': 'bandar-abbas',
    'یزد': 'yazd',
    'مرکزی': 'arak',
    'کرمانشاه': 'kermanshah',
    'همدان': 'hamedan',
    'لرستان': 'khorramabad',
    'بوشهر': 'bushehr',
    'زنجان': 'zanjan',
    'اردبیل': 'ardabil',
    'گلستان': 'gorgan',
    'سمنان': 'semnan',
    'قم': 'qom',
    'قزوین': 'qazvin',
    'سیستان و بلوچستان': 'zahedan',
    'کردستان': 'sanandaj',
    'ایلام': 'ilam',
    'چهارمحال و بختیاری': 'shahrekord',
    'کهگیلویه و بویراحمد': 'yasuj',
    'خراسان شمالی': 'bojnord',
    'خراسان جنوبی': 'birjand',
}

SENIORITY_MAP = {
    'junior': ['Junior', 'Intern', 'Trainee', 'Entry Level'],
    'mid': ['Mid-Level', 'Mid Level', 'Intermediate'],
    'senior': ['Senior', 'Lead', 'Expert', 'Principal'],
    'manager': ['Manager', 'Director', 'Head', 'VP'],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
}


def crawl_irantalent(keywords: str = '', city: str = '', level: str = 'all',
                       time_range: str = '7', max_pages: int = 2) -> list:
    """
    Crawl IranTalent via Playwright (Angular SPA).

    Returns list of dicts with normalized job data.
    """
    logger.info("IranTalent: Angular SPA, using Playwright...")
    return _crawl_via_playwright(keywords, city, level, time_range, max_pages)


def _crawl_via_playwright(keywords, city, level, time_range, max_pages):
    """Crawl IranTalent using Playwright with system Chrome."""
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
                "Install Chrome/Edge/Brave to crawl this platform."
            )
            return []

        page = bc.context.new_page()

        # Build URL: /en/jobs or /en/jobs/jobs-in-{city}
        if city and city in CITY_SLUGS:
            url = f"{JOBS_URL}/jobs-in-{CITY_SLUGS[city]}"
        else:
            url = JOBS_URL

        logger.info(f"IranTalent: navigating to {url}")
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            # Angular needs significant time to render
            page.wait_for_timeout(6000)
        except Exception as e:
            logger.error(f"IranTalent navigation failed: {e}")
            return []

        # Check if page loaded properly
        try:
            body_text = page.inner_text('body')
            if len(body_text.strip()) < 100:
                logger.warning("IranTalent: page body is nearly empty, site may be down")
                return []
        except Exception:
            pass

        results = []
        seen_urls = set()

        # Build keyword list for filtering
        search_terms = []
        if keywords and keywords.strip():
            search_terms = [kw.strip().lower() for kw in keywords.split() if kw.strip()]

        for pg in range(max_pages):
            try:
                # Wait for job links to appear (Angular renders them dynamically)
                try:
                    page.wait_for_selector(
                        'a[href*="/job/"]',
                        timeout=10000
                    )
                except Exception:
                    logger.info(f"IranTalent: no job links found on page {pg + 1}")

                # Extract all job links from the page
                all_links = page.query_selector_all('a[href*="/job/"]')

                if not all_links:
                    logger.info(f"IranTalent: no job cards on page {pg + 1}")
                    break

                # Each job link should have a numeric ID in the URL
                job_links = []
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if not href or href in seen_urls:
                        continue
                    # Must contain a numeric ID (e.g., /en/job/some-slug/178552)
                    if href.count('/') >= 3 and any(c.isdigit() for c in href):
                        seen_urls.add(href)
                        job_links.append((link, href))

                logger.info(f"IranTalent page {pg + 1}: found {len(job_links)} job links")

                for link_el, href in job_links:
                    try:
                        # Get the closest card/container parent
                        # IranTalent job cards are typically in a container with the link
                        card = link_el.evaluate_handle(
                            'el => el.closest("[class*=\"card\"], [class*=\"item\"], [class*=\"position\"], '
                            '[class*=\"listing\"], article, li, div[class]") || el.parentElement'
                        )
                        card_text = card.inner_text() if card else link_el.inner_text()

                        if len(card_text.strip()) < 15:
                            continue

                        # Extract title - usually the link text itself or an h2/h3 inside
                        title = ''
                        for sel in ['h2', 'h3', 'h4', '[class*="title"]', '[class*="name"]']:
                            title_el = link_el.query_selector(sel)
                            if title_el:
                                title = title_el.inner_text().strip()
                                break
                        if not title:
                            title = link_el.inner_text().strip()[:120]

                        if not title:
                            continue

                        # Extract company
                        company = ''
                        company_selectors = [
                            '[class*="company"]', '[class*="employer"]', '[class*="org"]',
                            '[class*="brand"]', '[class*="organization"]',
                        ]
                        if card:
                            for sel in company_selectors:
                                el = card.query_selector(sel)
                                if el:
                                    company = el.inner_text().strip()
                                    if company:
                                        break

                        # Extract location
                        city_name = city or ''
                        loc_selectors = [
                            '[class*="location"]', '[class*="city"]', '[class*="province"]',
                            '[class*="place"]',
                        ]
                        if card:
                            for sel in loc_selectors:
                                el = card.query_selector(sel)
                                if el:
                                    city_name = el.inner_text().strip()
                                    break

                        # Extract seniority level
                        seniority = ''
                        if card:
                            for sel in ['[class*="seniority"]', '[class*="level"]',
                                         '[class*="experience"]', '[class*="senior"]']:
                                el = card.query_selector(sel)
                                if el:
                                    seniority = el.inner_text().strip()
                                    break

                        # Extract job type
                        job_type = ''
                        if card:
                            for sel in ['[class*="type"]', '[class*="employment"]',
                                         '[class*="contract"]']:
                                el = card.query_selector(sel)
                                if el:
                                    job_type = el.inner_text().strip()
                                    break

                        # Extract skills
                        skills = []
                        if card:
                            for sel in ['[class*="skill"]', '[class*="tag"]', '[class*="tech"]']:
                                skill_els = card.query_selector_all(sel)
                                for s_el in skill_els:
                                    t = s_el.inner_text().strip()
                                    if t and t not in skills:
                                        skills.append(t)

                        # Extract salary if visible
                        salary = ''
                        if card:
                            for sel in ['[class*="salary"]', '[class*="compensation"]',
                                         '[class*="pay"]']:
                                el = card.query_selector(sel)
                                if el:
                                    salary = el.inner_text().strip()
                                    break

                        # Remote detection
                        is_remote = ('remote' in card_text.lower() or
                                     'دورکار' in card_text)

                        # Posted date
                        posted_date = ''
                        if card:
                            for sel in ['[class*="date"]', '[class*="time"]',
                                         '[class*="posted"]', '[class*="ago"]', 'time']:
                                el = card.query_selector(sel)
                                if el:
                                    posted_date = el.inner_text().strip()
                                    break

                        # Build full URL
                        if not href.startswith('http'):
                            href = f"{BASE_URL}{href}"

                        # Client-side keyword filtering
                        if search_terms:
                            combined = f"{title} {company} {card_text}".lower()
                            if not any(term in combined for term in search_terms):
                                continue

                        # Level filtering
                        if level != 'all':
                            level_kw = SENIORITY_MAP.get(level, [])
                            if level_kw:
                                full_text = f"{title} {seniority} {card_text}"
                                if not any(kw.lower() in full_text.lower() for kw in level_kw):
                                    continue

                        # Build description from available info
                        desc_parts = []
                        if seniority:
                            desc_parts.append(f"سطح: {seniority}")
                        if job_type:
                            desc_parts.append(f"نوع: {job_type}")
                        if skills:
                            desc_parts.append(f"مهارت‌ها: {', '.join(skills)}")
                        description = ' | '.join(desc_parts)

                        results.append({
                            'platform': 'irantalent',
                            'title': title,
                            'company': company,
                            'city': city_name,
                            'province': city_name,
                            'salary': salary,
                            'job_type': job_type,
                            'seniority_level': seniority,
                            'description': description,
                            'skills': skills,
                            'url': href,
                            'remote': is_remote,
                            'posted_date': posted_date,
                        })

                    except Exception as e:
                        logger.debug(f"IranTalent card parse error: {e}")
                        continue

                logger.info(f"IranTalent page {pg + 1}: {len(results)} total results")

                # Try pagination - look for "Load more" or next page button
                # IranTalent often uses "Load more" button or infinite scroll
                next_found = False

                # Try "Load more" button
                load_more_selectors = [
                    'button:has-text("Load more")',
                    'button:has-text("Show more")',
                    'a:has-text("Load more")',
                    'a:has-text("Show more")',
                    '[class*="load-more"]',
                    '[class*="show-more"]',
                ]
                for sel in load_more_selectors:
                    try:
                        btn = page.query_selector(sel)
                        if btn and btn.is_visible():
                            btn.click()
                            page.wait_for_timeout(4000)
                            next_found = True
                            break
                    except Exception:
                        continue

                if not next_found:
                    # Try traditional pagination
                    next_selectors = [
                        'a.next', 'button.next',
                        '[aria-label="Next"]', 'a[aria-label="next"]',
                        'li.next a', '[class*="pagination"] [class*="next"]',
                        'a:has-text("Next")', 'a:has-text("»")',
                    ]
                    for sel in next_selectors:
                        try:
                            btn = page.query_selector(sel)
                            if btn and btn.is_visible():
                                btn.click()
                                page.wait_for_timeout(4000)
                                next_found = True
                                break
                        except Exception:
                            continue

                if not next_found:
                    # Try scrolling down for infinite scroll
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(3000)

                    # Check if new content loaded
                    new_links = page.query_selector_all('a[href*="/job/"]')
                    new_urls = set()
                    for nl in new_links:
                        h = nl.get_attribute('href') or ''
                        if h.count('/') >= 3 and any(c.isdigit() for c in h) and h not in seen_urls:
                            new_urls.add(h)

                    if not new_urls:
                        logger.info("IranTalent: no more content, stopping pagination")
                        break

            except Exception as e:
                logger.error(f"IranTalent page {pg + 1} error: {e}")
                break

        logger.info(f"IranTalent total: {len(results)} jobs")
        return results

    finally:
        bc.__exit__(None, None, None)