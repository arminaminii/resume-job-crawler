"""
IranTalent crawler — uses their PUBLIC REST API.

API endpoint: POST https://api.irantalent.com/api/v1/employer/position/search-by-slug
Returns paginated JSON with job listings.

KEY INSIGHTS:
1. The endpoint name is 'search-by-slug' — it accepts a 'slug' param for category filtering
2. 'keyword' is for text search within/beside the category
3. 'location_slugs' for city filtering
4. 'created_at' field enables client-side time filtering
5. Seniority is a LIST: [{'title_farsi': 'کارشناس', 'title': 'Junior Professional'}]

RESPONSE STRUCTURE (data.data[i]):
  - title / title_farsi: job title
  - brand_data / employer: company info
  - location: city/province dict
  - seniority: list of seniority dicts
  - employment_type: job type dict
  - salary_from / salary_to: salary range
  - slug: for URL construction
  - role_description: HTML job description
  - created_at: ISO datetime string
  - is_remote: remote flag
  - job_category: list of category dicts
"""
import requests
import logging
import time
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

BASE_URL = "https://www.irantalent.com"
API_URL = "https://api.irantalent.com/api/v1/employer/position/search-by-slug"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.irantalent.com",
    "Referer": "https://www.irantalent.com/",
}

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
    'junior': ['Junior', 'Intern', 'Trainee', 'Entry Level', 'کارآموز', 'جونیور'],
    'mid': ['Mid-Level', 'Mid Level', 'Intermediate', 'متوسط', 'میان‌رده', 'کارشناس'],
    'senior': ['Senior', 'Lead', 'Expert', 'Principal', 'ارشد', 'سنیور', 'کارشناس ارشد'],
    'manager': ['Manager', 'Director', 'Head', 'VP', 'مدیر', 'سرپرست'],
}

API_TIMEOUT = 25


# Iran timezone (UTC+3:30)
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))


def _get_session():
    """Create a new requests Session for each call (thread-safe)."""
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _parse_salary(job_data: dict) -> str:
    """Parse salary from IranTalent API response.
    
    Salary values are raw numbers (e.g., 150000000 = 150 million Toman).
    """
    salary_from = job_data.get('salary_from')
    salary_to = job_data.get('salary_to')
    is_show = job_data.get('is_show_salary', False)

    if not is_show:
        return ''
    
    def to_millions(val):
        if not val:
            return None
        try:
            return int(val) / 1_000_000
        except (ValueError, TypeError):
            return None

    mf = to_millions(salary_from)
    mt = to_millions(salary_to)
    
    if mf and mt:
        return f"{int(mf)} - {int(mt)} میلیون تومان"
    elif mf:
        return f"از {int(mf)} میلیون تومان"
    elif mt:
        return f"تا {int(mt)} میلیون تومان"
    return ''


def _parse_seniority(seniority_data) -> str:
    """Parse seniority level from API response.
    
    seniority is a LIST of dicts: [{'title_farsi': 'کارشناس', 'id': 272, 'title': 'Junior Professional'}]
    """
    if not seniority_data:
        return ''
    if isinstance(seniority_data, list) and seniority_data:
        item = seniority_data[0]
        return (item.get('title_farsi', '') or item.get('title', '') or '')
    if isinstance(seniority_data, dict):
        return (seniority_data.get('title_farsi', '') or seniority_data.get('title', '') or '')
    return ''


def _parse_employment_type(emp_type: dict) -> str:
    """Parse employment type from API response."""
    if not emp_type:
        return ''
    return emp_type.get('title', '') or emp_type.get('title_farsi', '') or ''


def _parse_posted_date(created_at: str) -> str:
    """Parse ISO datetime to a Persian-friendly relative date string."""
    if not created_at:
        return ''
    try:
        # Handle various ISO formats
        if 'T' in created_at:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(created_at)
        
        # Make timezone-aware if naive
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IRAN_TZ)
        
        now = datetime.now(IRAN_TZ)
        diff = now - dt
        days = diff.days
        
        if days < 0:
            return ''
        elif days == 0:
            return 'امروز'
        elif days == 1:
            return 'دیروز'
        elif days < 7:
            return f'{days} روز پیش'
        elif days < 30:
            weeks = days // 7
            return f'{weeks} هفته پیش'
        elif days < 365:
            months = days // 30
            return f'{months} ماه پیش'
        else:
            return f'{days // 365} سال پیش'
    except (ValueError, TypeError):
        return created_at[:10] if created_at else ''


def _parse_datetime(created_at: str) -> datetime:
    """Parse ISO datetime to a timezone-aware datetime object for filtering."""
    if not created_at:
        return None
    try:
        if 'T' in created_at:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(created_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IRAN_TZ)
        return dt
    except (ValueError, TypeError):
        return None


def _job_matches_time(created_at: str, time_range: str) -> bool:
    """Check if job's posted date falls within the time range."""
    if not time_range or time_range == 'all':
        return True
    if not created_at:
        return True  # Can't filter without date
    
    try:
        days = int(time_range)
    except (ValueError, TypeError):
        return True
    
    dt = _parse_datetime(created_at)
    if dt is None:
        return True
    
    cutoff = datetime.now(IRAN_TZ) - timedelta(days=days)
    return dt >= cutoff


def _extract_skills_from_desc(role_description: str) -> list:
    """Extract meaningful text snippet from HTML description.
    
    Returns a short plain-text summary (not individual skills),
    suitable for display and client-side keyword matching.
    """
    if not role_description:
        return []
    import re
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', role_description)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    snippet = text[:200].strip()
    return [snippet] if snippet else []


def _job_matches_level(seniority_data, level: str) -> bool:
    """Check seniority level match.
    
    seniority is a LIST: [{'title_farsi': 'کارشناس', 'title': 'Junior Professional'}]
    """
    if not level or level == 'all':
        return True
    if not seniority_data:
        return True
    level_kw = SENIORITY_MAP.get(level, [])
    if not level_kw:
        return True
    # Get combined text from seniority list
    if isinstance(seniority_data, list):
        texts = []
        for item in seniority_data:
            if isinstance(item, dict):
                texts.append((item.get('title', '') or '').lower())
                texts.append((item.get('title_farsi', '') or '').lower())
        combined = ' '.join(texts)
    elif isinstance(seniority_data, dict):
        combined = f"{(seniority_data.get('title', '') or '').lower()} {(seniority_data.get('title_farsi', '') or '').lower()}"
    else:
        return True
    return any(kw.lower() in combined for kw in level_kw)


def crawl_irantalent(keywords: str = '', city: str = '', level: str = 'all',
                      time_range: str = '7', max_pages: int = 3,
                      category_slugs: list = None,
                      client_filter_keywords: list = None) -> list:
    """
    Crawl IranTalent via REST API.

    - keywords: user's search terms -> sent to API as 'keyword'
    - category_slugs: IranTalent category slugs -> sent as 'slug' for category filtering
    - city: Persian city name -> converted to slug for 'location_slugs'
    - level: seniority level for client-side filtering
    - time_range: max days ago (client-side filtering)
    - client_filter_keywords: additional category keywords for client-side filtering
    
    STRATEGY:
    1. Send 'slug' (first category slug) for category-based search
    2. Send 'keyword' (user's terms) for text refinement
    3. If no slug available, rely solely on keyword search
    4. Client-side: filter by level, time_range
    """
    results = []
    seen_ids = set()
    cfk = client_filter_keywords or []
    cat_slugs = category_slugs or []

    # Build request body
    body = {}

    # CRITICAL: Send 'slug' for category-based search (the endpoint IS search-by-slug)
    # Use the first category slug if available
    primary_slug = cat_slugs[0] if cat_slugs else ''
    if primary_slug:
        body['slug'] = primary_slug
        logger.info(f"IranTalent API: slug='{primary_slug}' (category filter)")

    # Keyword — send as text search alongside slug
    if keywords and keywords.strip():
        kw = ' '.join(keywords.strip().split()[:5])
        body['keyword'] = kw
        logger.info(f"IranTalent API: keyword='{kw}'")

    # City/location
    if city and city in CITY_SLUGS:
        body['location_slugs'] = [CITY_SLUGS[city]]

    logger.info(f"IranTalent: body keys={list(body.keys())}, city={city}, time_range={time_range}")

    for page_num in range(1, max_pages + 1):
        try:
            # Add page to body
            page_body = dict(body)
            page_body['page'] = page_num

            resp = _get_session().post(API_URL, json=page_body, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            # Response structure: {"data": {"data": [...], "total": N, "last_page": N, ...}}
            resp_data = data.get('data', {})
            if isinstance(resp_data, dict):
                jobs = resp_data.get('data', [])
                total = resp_data.get('total', 0)
                last_page = resp_data.get('last_page', 1)
            elif isinstance(resp_data, list):
                jobs = resp_data
                total = len(resp_data)
                last_page = 1
            else:
                logger.warning(f"IranTalent: unexpected response structure: {type(resp_data)}")
                break

            if page_num == 1:
                logger.info(f"IranTalent: {total} total jobs on platform for this query")

            if not jobs:
                logger.info(f"IranTalent: no more jobs at page {page_num}")
                break

            page_matched = 0
            for job in jobs:
                jid = job.get('id')
                if not jid or jid in seen_ids:
                    continue
                seen_ids.add(jid)

                # --- Time filtering (client-side) ---
                created_at = job.get('created_at', '') or ''
                if not _job_matches_time(created_at, time_range):
                    continue

                # --- Extract fields ---
                title = (job.get('title_farsi', '') or
                         job.get('title', '') or '')
                if not title:
                    continue

                # Company info — prefer 'employer' field over 'brand_data'
                employer = job.get('employer') or {}
                brand = job.get('brand_data') or {}
                company = (employer.get('name_farsi', '') or
                           brand.get('name_fa', '') or
                           employer.get('name', '') or
                           brand.get('name_en', '') or
                           brand.get('company_legal_name_fa', '') or '')

                # Location — prefer location_text_farsi (Persian)
                loc_data = job.get('location') or {}
                location_text = (job.get('location_text_farsi', '') or
                                job.get('location_text', '') or '')
                city_name = ''
                province_name = ''
                if loc_data and isinstance(loc_data, dict):
                    city_name = loc_data.get('title_farsi', '') or loc_data.get('title', '') or ''
                    parent = loc_data.get('parent') or {}
                    province_name = (parent.get('title_farsi', '') or
                                    parent.get('title', '') or '')
                if not city_name and location_text:
                    city_name = location_text

                # Salary
                salary = _parse_salary(job)

                # Seniority
                seniority_data = job.get('seniority')
                seniority = _parse_seniority(seniority_data)

                # Employment type
                emp_type = job.get('employment_type') or {}
                job_type = _parse_employment_type(emp_type)

                # Remote / work type
                work_type_raw = job.get('work_type', '') or ''
                is_remote = (work_type_raw == 'remote' or
                            job.get('is_remote', False))
                if not job_type and work_type_raw:
                    wt_map = {'on_site': 'حضوری', 'remote': 'دورکاری', 'hybrid': 'ترکیبی'}
                    job_type = wt_map.get(work_type_raw, work_type_raw)

                # Posted date (human-readable)
                posted_date = _parse_posted_date(created_at)

                # Skills — extract from job categories + description
                skills = []
                # Add job categories as context
                for cat in (job.get('job_category') or []):
                    if isinstance(cat, dict):
                        cat_title = cat.get('title_farsi', '') or cat.get('title', '')
                        if cat_title:
                            skills.append(cat_title)
                # Extract skills from description
                desc_html = (job.get('role_description_farsi', '') or
                            job.get('role_description', '') or '')
                desc_skills = _extract_skills_from_desc(desc_html)
                if desc_skills:
                    skills.append(desc_skills)
                desc_text = ' '.join(desc_skills) if desc_skills else ''

                # Build URL
                slug = job.get('slug', '')
                url = f"{BASE_URL}/jobs/{slug}" if slug else f"{BASE_URL}/jobs/{jid}"

                # --- Level filtering ---
                if not _job_matches_level(seniority_data, level):
                    continue

                page_matched += 1

                # Build description
                desc_parts = []
                if seniority:
                    desc_parts.append(f"سطح: {seniority}")
                if job_type:
                    desc_parts.append(f"نوع: {job_type}")
                # Add company industry/size
                industry = brand.get('industry', {})
                if isinstance(industry, dict):
                    ind_title = industry.get('title_farsi', '') or industry.get('title', '')
                    if ind_title:
                        desc_parts.append(f"صنعت: {ind_title}")
                company_size = brand.get('company_size', {})
                if isinstance(company_size, dict):
                    cs_title = company_size.get('title_farsi', '') or company_size.get('title', '')
                    if cs_title:
                        desc_parts.append(f"اندازه: {cs_title}")
                description = ' | '.join(desc_parts)

                results.append({
                    'platform': 'irantalent',
                    'title': title,
                    'company': company,
                    'city': city_name,
                    'province': province_name,
                    'salary': salary,
                    'job_type': job_type,
                    'seniority_level': seniority,
                    'description': description,
                    'skills': skills,
                    'url': url,
                    'remote': is_remote,
                    'posted_date': posted_date,
                })

            logger.info(f"IranTalent page {page_num}: {len(jobs)} API, "
                        f"{page_matched} matched (total: {len(results)})")

            if page_num >= last_page:
                logger.info(f"IranTalent: reached last page ({last_page})")
                break

            time.sleep(0.5)

        except requests.Timeout:
            logger.error(f"IranTalent timeout at page {page_num}")
            break
        except requests.ConnectionError as e:
            logger.error(f"IranTalent connection error: {e}")
            break
        except Exception as e:
            logger.error(f"IranTalent error at page {page_num}: {e}")
            break

    logger.info(f"IranTalent total: {len(results)} jobs")
    return results
