"""
IranTalent crawler — uses Playwright with system Chrome.

IranTalent (irantalent.com) is an Angular SPA with NO reliable public job search API.
Strategy:
1. Search via URL query parameter: /en/jobs?keyword=...
2. Wait for Angular to render job cards
3. Extract from rendered DOM using multiple selector strategies
4. Handle pagination via "Load more" / infinite scroll

SELECTOR STRATEGY:
- Primary: Find all <a> links matching /job/ pattern
- For each link, find the closest container/card
- Extract data using role-based and class-based selectors
- Fallback: Parse raw text if structured selectors fail
"""
import logging
import time
from urllib.parse import quote

logger = logging.getLogger(__name__)

BASE_URL = "https://www.irantalent.com"
JOBS_URL = f"{BASE_URL}/en/jobs"

CITY_SLUGS = {
    'تهران': 'tehran', 'اصفهان': 'isfahan', 'البرز': 'alborz',
    'خراسان رضوی': 'mashhad', 'فارس': 'shiraz', 'خوزستان': 'ahvaz',
    'گیلان': 'rasht', 'مازندران': 'sari', 'آذربایجان شرقی': 'tabriz',
    'آذربایجان غربی': 'urmia', 'کرمان': 'kerman', 'هرمزگان': 'bandar-abbas',
    'یزد': 'yazd', 'مرکزی': 'arak', 'کرمانشاه': 'kermanshah',
    'همدان': 'hamedan', 'لرستان': 'khorramabad', 'بوشهر': 'bushehr',
    'زنجان': 'zanjan', 'اردبیل': 'ardabil', 'گلستان': 'gorgan',
    'سمنان': 'semnan', 'قم': 'qom', 'قزوین': 'qazvin',
    'سیستان و بلوچستان': 'zahedan', 'کردستان': 'sanandaj',
    'ایلام': 'ilam', 'چهارمحال و بختیاری': 'shahrekord',
    'کهگیلویه و بویراحمد': 'yasuj', 'خراسان شمالی': 'bojnord',
    'خراسان جنوبی': 'birjand',
}

SENIORITY_MAP = {
    'junior': ['Junior', 'Intern', 'Trainee', 'Entry Level'],
    'mid': ['Mid-Level', 'Mid Level', 'Intermediate'],
    'senior': ['Senior', 'Lead', 'Expert', 'Principal'],
    'manager': ['Manager', 'Director', 'Head', 'VP'],
}

HEADERS_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def _try_extract(el, selectors: list) -> str:
    """Try multiple CSS selectors, return first match's text."""
    for sel in selectors:
        try:
            found = el.query_selector(sel)
            if found:
                text = found.inner_text().strip()
                if text:
                    return text
        except Exception:
            continue
    return ''


def _try_extract_all(el, selectors: list) -> list:
    """Try multiple CSS selectors, return all matching texts."""
    texts = []
    seen = set()
    for sel in selectors:
        try:
            els = el.query_selector_all(sel)
            for e in els:
                t = e.inner_text().strip()
                if t and t not in seen and len(t) < 60:
                    seen.add(t)
                    texts.append(t)
        except Exception:
            continue
    return texts


def crawl_irantalent(keywords: str = '', city: str = '', level: str = 'all',
                        time_range: str = '7', max_pages: int = 3,
                        client_filter_keywords: list = None) -> list:
    """Crawl IranTalent via Playwright (Angular SPA)."""
    logger.info("IranTalent: starting Playwright crawl...")
    return _crawl_via_playwright(
        keywords=keywords, city=city, level=level,
        time_range=time_range, max_pages=max_pages,
        client_filter_keywords=client_filter_keywords or [],
    )


def _crawl_via_playwright(keywords, city, level, time_range, max_pages, client_filter_keywords):
    """Crawl IranTalent using Playwright with system Chrome."""
    from .playwright_helper import BrowserContext

    bc = BrowserContext(headless=True, user_agent=HEADERS_UA, locale='en-US')

    try:
        bc.__enter__()
        if not bc.is_available:
            logger.warning("IranTalent: No browser available.")
            return []

        page = bc.context.new_page()

        # Build URL with keyword search
        if city and city in CITY_SLUGS:
            base = f"{JOBS_URL}/jobs-in-{CITY_SLUGS[city]}"
        else:
            base = JOBS_URL

        # Add keyword as query parameter
        if keywords and keywords.strip():
            # Take first 3 words
            kw = ' '.join(keywords.strip().split()[:3])
            url = f"{base}?keyword={quote(kw)}"
        else:
            url = base

        logger.info(f"IranTalent: navigating to {url}")
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            # Angular needs time to render
            page.wait_for_timeout(5000)
        except Exception as e:
            logger.error(f"IranTalent navigation failed: {e}")
            return []

        # Check page loaded
        try:
            body_text = page.inner_text('body')
            if len(body_text.strip()) < 100:
                logger.warning("IranTalent: page nearly empty")
                return []
        except Exception:
            pass

        results = []
        seen_urls = set()

        for pg in range(max_pages):
            try:
                # Wait for job links
                try:
                    page.wait_for_selector('a[href*="/job/"]', timeout=12000)
                except Exception:
                    logger.info(f"IranTalent pg {pg+1}: no job links")

                all_links = page.query_selector_all('a[href*="/job/"]')
                if not all_links:
                    logger.info(f"IranTalent pg {pg+1}: empty")
                    break

                # Filter links with numeric IDs
                job_links = []
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if not href or href in seen_urls:
                        continue
                    if href.count('/') >= 3 and any(c.isdigit() for c in href):
                        seen_urls.add(href)
                        job_links.append((link, href))

                logger.info(f"IranTalent pg {pg+1}: {len(job_links)} job links")

                for link_el, href in job_links:
                    try:
                        # Get the card container - try multiple strategies
                        card = link_el.evaluate_handle(
                            'el => el.closest("article, [class*=\"card\"], [class*=\"item\"], '
                            '[class*=\"listing\"], [class*=\"position\"], li, div[class]") '
                            '|| el.parentElement'
                        )
                        card_text = card.inner_text() if card else link_el.inner_text()

                        if len(card_text.strip()) < 15:
                            continue

                        # --- Extract fields using MULTIPLE selector strategies ---

                        # Title: try h2/h3/h4 first, then link text, then card first line
                        title = _try_extract(link_el, ['h2', 'h3', 'h4',
                                    '[class*="title"]', '[class*="name"]',
                                    '[class*="position-title"]', '[class*="job-title"]'])
                        if not title:
                            title = link_el.inner_text().strip().split('\n')[0].strip()[:120]
                        if not title:
                            continue

                        # Company
                        company = _try_extract(card, [
                            '[class*="company"]', '[class*="employer"]', '[class*="org"]',
                            '[class*="brand"]', '[class*="organization"]',
                            '[class*="company-name"]',
                        ]) if card else ''

                        # Location
                        city_name = city or ''
                        if card:
                            loc = _try_extract(card, [
                                '[class*="location"]', '[class*="city"]',
                                '[class*="province"]', '[class*="place"]',
                            ])
                            if loc:
                                city_name = loc

                        # Seniority
                        seniority = ''
                        if card:
                            seniority = _try_extract(card, [
                                '[class*="seniority"]', '[class*="level"]',
                                '[class*="experience"]', '[class*="senior"]',
                                '[class*="career-level"]',
                            ])

                        # Job type
                        job_type = ''
                        if card:
                            job_type = _try_extract(card, [
                                '[class*="type"]', '[class*="employment"]',
                                '[class*="contract"]', '[class*="job-type"]',
                            ])

                        # Skills
                        skills = []
                        if card:
                            skills = _try_extract_all(card, [
                                '[class*="skill"]', '[class*="tag"]',
                                '[class*="tech"]', '[class*="badge"]',
                            ])

                        # Salary
                        salary = ''
                        if card:
                            salary = _try_extract(card, [
                                '[class*="salary"]', '[class*="compensation"]',
                                '[class*="pay"]', '[class*="range"]',
                            ])

                        # Remote detection
                        is_remote = ('remote' in card_text.lower() or
                                    'دورکار' in card_text)

                        # Posted date
                        posted_date = ''
                        if card:
                            posted_date = _try_extract(card, [
                                '[class*="date"]', '[class*="time"]',
                                '[class*="posted"]', '[class*="ago"]', 'time',
                            ])

                        # Build full URL
                        if not href.startswith('http'):
                            href = f"{BASE_URL}{href}"

                        # --- Client-side filtering ---
                        # Keyword filtering
                        if keywords and keywords.strip():
                            kw_list = [k.strip().lower() for k in keywords.split() if k.strip()]
                            combined = f"{title} {company} {card_text}".lower()
                            if not any(term in combined for term in kw_list):
                                continue

                        # Category-based client filtering
                        if client_filter_keywords:
                            combined_all = f"{title} {company} {' '.join(skills)} {card_text}".lower()
                            if not any(kw.lower() in combined_all for kw in client_filter_keywords):
                                continue

                        # Level filtering
                        if level != 'all':
                            level_kw = SENIORITY_MAP.get(level, [])
                            if level_kw:
                                full_text = f"{title} {seniority} {card_text}"
                                if not any(kw.lower() in full_text.lower() for kw in level_kw):
                                    continue

                        # Build description
                        desc_parts = []
                        if seniority:
                            desc_parts.append(f"سطح: {seniority}")
                        if job_type:
                            desc_parts.append(f"نوع: {job_type}")
                        if skills:
                            desc_parts.append(f"مهارت‌ها: {', '.join(skills[:5])}")
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

                logger.info(f"IranTalent pg {pg+1}: {len(results)} total results")

                # --- Pagination ---
                next_found = False

                # Try "Load more" / "Show more" buttons
                for sel in ['button:has-text("Load more")', 'button:has-text("Show more")',
                           'a:has-text("Load more")', 'a:has-text("Show more")',
                           '[class*="load-more"]', '[class*="show-more"]']:
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
                    # Try next page buttons
                    for sel in ['a.next', 'button.next', '[aria-label="Next"]',
                               'a[aria-label="next"]', 'a:has-text("Next")',
                               'a:has-text("»")']:
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
                    # Try infinite scroll
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(3000)

                    new_links = page.query_selector_all('a[href*="/job/"]')
                    new_count = 0
                    for nl in new_links:
                        h = nl.get_attribute('href') or ''
                        if h.count('/') >= 3 and any(c.isdigit() for c in h) and h not in seen_urls:
                            new_count += 1

                    if new_count == 0:
                        logger.info("IranTalent: no more content")
                        break

            except Exception as e:
                logger.error(f"IranTalent pg {pg+1} error: {e}")
                break

        logger.info(f"IranTalent total: {len(results)} jobs")
        return results

    finally:
        bc.__exit__(None, None, None)