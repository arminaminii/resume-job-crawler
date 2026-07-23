"""
IranTalent crawler — uses their PUBLIC REST API.

API endpoint: POST https://api.irantalent.com/api/v1/employer/position/search-by-slug

RESEARCH FINDINGS (tested 2026-07-23):
1. 'slug' param is COMPLETELY IGNORED — all slugs return same 1730 jobs
2. 'keyword' WORKS — returns relevant subset (e.g. 'python'=54)
3. 'location_slugs' WORKS for city filtering  
4. 'created_at' = date-only '2026-07-08' (no time)
5. 'lived_at' = datetime '2026-07-23 10:19:44' (PRECISE - use this!)
6. No keyword or empty keyword = 0 results (must have keyword)
7. API caps at 30 per page regardless of per_page param
8. 'job_category' contains categories (e.g. 'Marketing'), NOT skills
9. 'seniority' contains level data like {'title_farsi': 'کارمند / کارشناس'}
10. 'brand_data' has 'industry' dict with title_farsi

STRATEGY:
- Use 'keyword' for search (only working search param)
- Use 'lived_at' (datetime) for PRECISE time filtering
- Search each keyword separately and MERGE for more results
- Extract real skills from description + category, not just category name
- Client-side relevance scoring (title match >> description match)
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

# Mapping from our level keys to what IranTalent API actually returns
SENIORITY_MAP = {
    'junior': ['junior', 'intern', 'trainee', 'entry level', 'کارآموز', 'جونیور',
               'کارمند / کارشناس', 'junior professional'],
    'mid': ['mid-level', 'mid level', 'intermediate', 'متوسط', 'میان‌رده',
            'کارشناس ارشد / متخصص', 'senior professional'],
    'senior': ['senior', 'lead', 'expert', 'principal', 'ارشد', 'سنیور',
               'کارشناس ارشد', 'تخصص بالا'],
    'manager': ['manager', 'director', 'head', 'vp', 'مدیر', 'سرپرست', 'مدیر میانی'],
}

API_TIMEOUT = 25
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))


def _get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _parse_lived_at(lived_at: str) -> datetime:
    """Parse '2026-07-23 10:19:44' format to datetime."""
    if not lived_at:
        return None
    try:
        return datetime.strptime(lived_at[:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=IRAN_TZ)
    except (ValueError, TypeError):
        return None


def _parse_posted_date(lived_at: str) -> str:
    """Convert lived_at to human-readable Persian relative date."""
    dt = _parse_lived_at(lived_at)
    if not dt:
        return ''
    now = datetime.now(IRAN_TZ)
    diff_seconds = (now - dt).total_seconds()
    if diff_seconds < 0:
        return ''
    diff_hours = diff_seconds / 3600
    diff_days = diff_seconds / 86400
    if diff_hours < 1:
        return 'لحظاتی پیش'
    elif diff_hours < 24:
        hours = int(diff_hours)
        return f'{hours} ساعت پیش'
    elif diff_days < 2:
        return 'دیروز'
    elif diff_days < 7:
        return f'{int(diff_days)} روز پیش'
    elif diff_days < 30:
        return f'{int(diff_days) // 7} هفته پیش'
    elif diff_days < 365:
        return f'{int(diff_days) // 30} ماه پیش'
    else:
        return f'{int(diff_days) // 365} سال پیش'


def _job_matches_time(lived_at: str, time_range: str) -> bool:
    """Use lived_at (datetime) for PRECISE time filtering."""
    if not time_range or time_range == 'all':
        return True
    if not lived_at:
        return True
    try:
        max_days = int(time_range)
    except (ValueError, TypeError):
        return True
    dt = _parse_lived_at(lived_at)
    if not dt:
        return True
    cutoff = datetime.now(IRAN_TZ) - timedelta(days=max_days)
    return dt >= cutoff


def _job_matches_level(seniority_data, level: str) -> bool:
    """Check if job's seniority matches the requested level."""
    if not level or level == 'all':
        return True
    if not seniority_data:
        return True  # Don't filter out if no data
    level_kws = SENIORITY_MAP.get(level, [])
    if not level_kws:
        return True
    if isinstance(seniority_data, list):
        texts = []
        for item in seniority_data:
            if isinstance(item, dict):
                texts.append((item.get('title', '') or '').lower())
                texts.append((item.get('title_farsi', '') or '').lower())
                texts.append((item.get('slug', '') or '').lower())
        combined = ' '.join(texts)
    elif isinstance(seniority_data, dict):
        combined = f"{(seniority_data.get('title', '') or '').lower()} {(seniority_data.get('title_farsi', '') or '').lower()}"
    else:
        return True
    # Check if ANY level keyword matches
    return any(kw.lower() in combined for kw in level_kws)


def _extract_skills_from_desc(desc_html: str, max_skills: int = 8) -> list:
    """Extract skill-like words from job description HTML."""
    if not desc_html:
        return []
    text = re.sub(r'<[^>]+>', ' ', desc_html)
    # Look for common skill patterns
    skill_patterns = [
        r'(?:به\s+)?(?:آشنایی|تسلط|مسلط|ماهر|آگاهی)\s+(?:به\s+)?([^،.\n]{2,30}?)(?:[,،.\n]|$)',
    ]
    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text)
        skills.extend([m.strip() for m in matches if len(m.strip()) > 2])
    return list(set(skills[:max_skills]))


def _calc_relevance(job: dict, search_keywords: list) -> float:
    """Calculate relevance score. Title match = 5, description = 0.5."""
    if not search_keywords:
        return job.get('_score', 0) or 0
    
    score = 0.0
    kw_lower = [k.lower() for k in search_keywords]
    
    title_en = (job.get('title', '') or '').lower()
    title_fa = (job.get('title_farsi', '') or '').lower()
    for kw in kw_lower:
        if kw in title_en:
            score += 5
        if kw in title_fa:
            score += 5
    
    # Check short_title equivalent
    desc_html = (job.get('role_description_farsi', '') or 
                job.get('role_description', '') or '')
    desc_text = re.sub(r'<[^>]+>', ' ', desc_html).lower()
    for kw in kw_lower:
        if kw in desc_text:
            score += 0.5
    
    # Also check job_category titles
    for cat in (job.get('job_category') or []):
        if isinstance(cat, dict):
            cat_text = ((cat.get('title', '') or '') + ' ' + 
                       (cat.get('title_farsi', '') or '')).lower()
            for kw in kw_lower:
                if kw in cat_text:
                    score += 1
    
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


def crawl_irantalent(keywords: str = '', city: str = '', level: str = 'all',
                      time_range: str = '7', max_pages: int = 3,
                      category_slugs: list = None,
                      client_filter_keywords: list = None) -> list:
    """
    Crawl IranTalent via REST API.
    
    STRATEGY: 
    - Search each keyword separately and merge (more results)
    - Use lived_at (datetime) for precise time filtering
    - Client-side relevance scoring
    """
    results = []
    seen_ids = set()
    search_kws = [k.strip() for k in (keywords or '').split() if k.strip()]
    
    # If no keywords, use client_filter_keywords
    if not search_kws and client_filter_keywords:
        search_kws = [k.strip().lower() for k in client_filter_keywords[:3]]
    
    # Determine which keyword queries to run
    if not search_kws:
        logger.warning("IranTalent: no keywords provided, cannot search (API requires keyword)")
        return []
    
    # Search with each keyword separately for maximum coverage
    # But limit to top 3 keywords to avoid too many API calls
    kw_queries = search_kws[:3]
    
    for kw in kw_queries:
        body = {'keyword': kw, 'page': 1}
        if city and city in CITY_SLUGS:
            body['location_slugs'] = [CITY_SLUGS[city]]
        
        for page_num in range(1, 20):  # max 20 pages per keyword
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
                
                if page_num == 1 and kw == kw_queries[0]:
                    logger.info(f"IranTalent: {total} total for keyword='{kw}'")
                
                if not jobs:
                    break
                
                for job in jobs:
                    jid = job.get('id')
                    if not jid or jid in seen_ids:
                        continue
                    seen_ids.add(jid)
                    
                    # Use lived_at for precise time filtering
                    lived_at = job.get('lived_at', '') or ''
                    if not _job_matches_time(lived_at, time_range):
                        continue
                    
                    title = (job.get('title_farsi', '') or job.get('title', '') or '')
                    if not title:
                        continue
                    
                    employer = job.get('employer') or {}
                    brand = job.get('brand_data') or {}
                    company = (employer.get('name_farsi', '') or
                               brand.get('name_fa', '') or
                               employer.get('name', '') or
                               brand.get('name_en', '') or
                               brand.get('company_legal_name_fa', '') or '')
                    
                    loc_data = job.get('location') or {}
                    city_name = (loc_data.get('title_farsi', '') or
                                 loc_data.get('title', '') or
                                 job.get('location_text_farsi', '') or '')
                    
                    salary = _parse_salary(job)
                    
                    # Seniority level
                    seniority_data = job.get('seniority')
                    seniority = ''
                    if isinstance(seniority_data, list) and seniority_data:
                        seniority = (seniority_data[0].get('title_farsi', '') or
                                    seniority_data[0].get('title', '') or '')
                    elif isinstance(seniority_data, dict):
                        seniority = seniority_data.get('title_farsi', '') or ''
                    
                    # Employment type
                    emp_type = job.get('employment_type') or {}
                    job_type = emp_type.get('title_farsi', '') or emp_type.get('title', '') or ''
                    
                    # Remote check
                    work_type_raw = job.get('work_type', '') or ''
                    is_remote = work_type_raw == 'remote'
                    
                    # Posted date from lived_at (precise)
                    posted_date = _parse_posted_date(lived_at)
                    
                    # Skills: extract from categories + description
                    skills = []
                    for cat in (job.get('job_category') or []):
                        if isinstance(cat, dict):
                            cat_title = cat.get('title_farsi', '') or cat.get('title', '')
                            if cat_title:
                                skills.append(cat_title)
                    # Also extract skill-like phrases from description
                    desc_skills = _extract_skills_from_desc(
                        job.get('role_description_farsi', '') or '')
                    skills.extend(desc_skills)
                    
                    slug = job.get('slug', '')
                    url = f"{BASE_URL}/jobs/{slug}" if slug else f"{BASE_URL}/jobs/{jid}"
                    
                    # Level filtering
                    if not _job_matches_level(seniority_data, level):
                        continue
                    
                    # Relevance scoring
                    relevance = _calc_relevance(job, search_kws)
                    
                    # Build description
                    desc_parts = []
                    if seniority:
                        desc_parts.append(f"سطح: {seniority}")
                    if job_type:
                        desc_parts.append(f"نوع: {job_type}")
                    industry = brand.get('industry')
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
                        'province': '',
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
                logger.error(f"IranTalent timeout at page {page_num} for kw='{kw}'")
                break
            except requests.ConnectionError as e:
                logger.error(f"IranTalent connection error: {e}")
                break
            except Exception as e:
                logger.error(f"IranTalent error at page {page_num}: {e}")
                break
    
    # Sort by relevance, deduplicate
    results.sort(key=lambda x: x.get('_relevance', 0), reverse=True)
    for r in results:
        r.pop('_relevance', None)
    
    logger.info(f"IranTalent total: {len(results)} jobs")
    return results
