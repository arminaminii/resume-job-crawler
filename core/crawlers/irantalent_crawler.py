"""
IranTalent crawler — uses their PUBLIC REST API.

API endpoint: POST https://api.irantalent.com/api/v1/employer/position/search-by-slug

CRITICAL RESEARCH FINDINGS (tested 2026-07-22):
1. 'slug' parameter is COMPLETELY IGNORED — always returns same ~1728 jobs
2. 'keyword' WORKS — returns different totals (e.g. 'python'=54, 'react'=28)
3. BUT keyword searches FULL DESCRIPTION, not just title (low relevance)
4. 'location_slugs' WORKS for city filtering
5. 'created_at' is date-only string '2026-07-08' (no time)
6. '_score' and 'matching_score' fields indicate Elasticsearch backend
7. Response has 50+ fields per job including rich data

STRATEGY:
- Use 'keyword' for search (the only working param besides location)
- Fetch many pages for comprehensive results
- Add client-side TIME filtering based on 'created_at' date
- Add client-side RELEVANCE SCORING (title match >> description match)
- Sort results by relevance score (most relevant first)
"""
import requests
import logging
import time
import re
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
    'junior': ['Junior', 'Intern', 'Trainee', 'Entry Level', 'کارآموز', 'جونیور', 'کارمند / کارشناس'],
    'mid': ['Mid-Level', 'Mid Level', 'Intermediate', 'متوسط', 'میان‌رده', 'کارشناس ارشد / متخصص'],
    'senior': ['Senior', 'Lead', 'Expert', 'Principal', 'ارشد', 'سنیور', 'کارشناس ارشد'],
    'manager': ['Manager', 'Director', 'Head', 'VP', 'مدیر', 'سرپرست', 'مدیر میانی'],
}

API_TIMEOUT = 25
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))


def _get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _calc_relevance(job: dict, search_keywords: list) -> float:
    """
    Calculate relevance score for a job.
    Title match = 5 points, title_farsi match = 5 points.
    Description keyword match = 0.5 per keyword.
    _score from API = bonus.
    """
    if not search_keywords:
        return job.get('_score', 0) or 0
    
    score = 0.0
    kw_lower = [k.lower() for k in search_keywords]
    
    # Title matches (highest weight)
    title_en = (job.get('title', '') or '').lower()
    title_fa = (job.get('title_farsi', '') or '').lower()
    for kw in kw_lower:
        if kw in title_en:
            score += 5
        if kw in title_fa:
            score += 5
    
    # Description matches (lower weight)
    desc_html = (job.get('role_description_farsi', '') or 
                job.get('role_description', '') or '')
    desc_text = re.sub(r'<[^>]+>', ' ', desc_html).lower()
    for kw in kw_lower:
        if kw in desc_text:
            score += 0.5
    
    # API's own score as small bonus
    api_score = job.get('_score', 0) or 0
    score += api_score * 0.01
    
    return score


def _parse_salary(job_data: dict) -> str:
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


def _parse_posted_date(created_at: str) -> str:
    if not created_at:
        return ''
    try:
        # created_at is '2026-07-08' (date only)
        dt = datetime.strptime(created_at[:10], '%Y-%m-%d').replace(tzinfo=IRAN_TZ)
        now = datetime.now(IRAN_TZ)
        diff = (now - dt).days
        if diff < 0:
            return ''
        elif diff == 0:
            return 'امروز'
        elif diff == 1:
            return 'دیروز'
        elif diff < 7:
            return f'{diff} روز پیش'
        elif diff < 30:
            return f'{diff // 7} هفته پیش'
        elif diff < 365:
            return f'{diff // 30} ماه پیش'
        else:
            return f'{diff // 365} سال پیش'
    except (ValueError, TypeError):
        return created_at[:10] if created_at else ''


def _job_matches_time(created_at: str, time_range: str) -> bool:
    if not time_range or time_range == 'all':
        return True
    if not created_at:
        return True
    try:
        max_days = int(time_range)
    except (ValueError, TypeError):
        return True
    try:
        dt = datetime.strptime(created_at[:10], '%Y-%m-%d').replace(tzinfo=IRAN_TZ)
        cutoff = datetime.now(IRAN_TZ) - timedelta(days=max_days)
        return dt >= cutoff
    except (ValueError, TypeError):
        return True


def _job_matches_level(seniority_data, level: str) -> bool:
    if not level or level == 'all':
        return True
    if not seniority_data:
        return True
    level_kw = SENIORITY_MAP.get(level, [])
    if not level_kw:
        return True
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
    
    STRATEGY: keyword-only search, client-side time + relevance filtering.
    """
    results = []
    seen_ids = set()
    search_kws = [k.strip().lower() for k in (keywords or '').split() if k.strip()]

    # Build request body — keyword ONLY (slug is ignored)
    body = {}
    if keywords and keywords.strip():
        kw = ' '.join(keywords.strip().split()[:5])
        body['keyword'] = kw
        logger.info(f"IranTalent API: keyword='{kw}'")

    if city and city in CITY_SLUGS:
        body['location_slugs'] = [CITY_SLUGS[city]]

    # Fetch more pages for comprehensive results
    effective_pages = max(max_pages * 3, 10)

    for page_num in range(1, effective_pages + 1):
        try:
            page_body = dict(body)
            page_body['page'] = page_num

            resp = _get_session().post(API_URL, json=page_body, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

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
                break

            if page_num == 1:
                logger.info(f"IranTalent: {total} total jobs for keyword")

            if not jobs:
                break

            for job in jobs:
                jid = job.get('id')
                if not jid or jid in seen_ids:
                    continue
                seen_ids.add(jid)

                created_at = job.get('created_at', '') or ''

                # --- Time filtering ---
                if not _job_matches_time(created_at, time_range):
                    continue

                title = (job.get('title_farsi', '') or job.get('title', '') or '')
                if not title:
                    continue

                employer = job.get('employer') or {}
                brand = job.get('brand_data') or {}
                company = (employer.get('name_farsi', '') or
                           brand.get('name_fa', '') or
                           employer.get('name', '') or
                           brand.get('name_en', '') or '')

                loc_data = job.get('location') or {}
                city_name = (loc_data.get('title_farsi', '') or
                             loc_data.get('title', '') or
                             job.get('location_text_farsi', '') or '')
                province_name = ''
                parent = loc_data.get('parent') or {}
                if isinstance(parent, dict):
                    province_name = parent.get('title_farsi', '') or parent.get('title', '') or ''

                salary = _parse_salary(job)
                seniority_data = job.get('seniority')
                seniority = ''
                if isinstance(seniority_data, list) and seniority_data:
                    seniority = (seniority_data[0].get('title_farsi', '') or
                                seniority_data[0].get('title', '') or '')

                emp_type = job.get('employment_type') or {}
                job_type = emp_type.get('title_farsi', '') or emp_type.get('title', '') or ''
                work_type_raw = job.get('work_type', '') or ''
                is_remote = work_type_raw == 'remote' or job.get('is_remote', False)

                posted_date = _parse_posted_date(created_at)

                # Skills
                skills = []
                for cat in (job.get('job_category') or []):
                    if isinstance(cat, dict):
                        cat_title = cat.get('title_farsi', '') or cat.get('title', '')
                        if cat_title:
                            skills.append(cat_title)

                slug = job.get('slug', '')
                url = f"{BASE_URL}/jobs/{slug}" if slug else f"{BASE_URL}/jobs/{jid}"

                # --- Level filtering ---
                if not _job_matches_level(seniority_data, level):
                    continue

                # --- Relevance scoring ---
                relevance = _calc_relevance(job, search_kws)

                # Build description
                desc_parts = []
                if seniority:
                    desc_parts.append(f"سطح: {seniority}")
                if job_type:
                    desc_parts.append(f"نوع: {job_type}")
                industry = brand.get('industry', {})
                if isinstance(industry, dict):
                    ind_title = industry.get('title_farsi', '') or industry.get('title', '')
                    if ind_title:
                        desc_parts.append(f"صنعت: {ind_title}")
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
                    '_relevance': relevance,
                })

            if page_num >= last_page:
                break
            time.sleep(0.4)

        except requests.Timeout:
            logger.error(f"IranTalent timeout at page {page_num}")
            break
        except requests.ConnectionError as e:
            logger.error(f"IranTalent connection error: {e}")
            break
        except Exception as e:
            logger.error(f"IranTalent error at page {page_num}: {e}")
            break

    # Sort by relevance (most relevant first)
    results.sort(key=lambda x: x.get('_relevance', 0), reverse=True)
    for r in results:
        r.pop('_relevance', None)

    logger.info(f"IranTalent total: {len(results)} jobs")
    return results
