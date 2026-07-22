"""
Jobvision crawler — uses their REST API.

API endpoint: POST https://candidateapi.jobvision.ir/api/v1/JobPost/List

CRITICAL RESEARCH FINDINGS (tested 2026-07-22):
1. 'categorySlugs' in filters is COMPLETELY IGNORED — always returns all jobs
2. 'keyword' (top-level) WORKS — returns relevant results (e.g. 'python' → 663 results)
3. 'publishedDateGte' in filters is IGNORED — must use client-side filtering
4. Maximum 30 results per page regardless of pageSize
5. 'activationTime.passedDays' gives days since posting — perfect for client-side time filter
6. 'sort' values don't seem to affect results (all return same order)

STRATEGY:
- Send 'keyword' at top-level for server-side text search
- DO NOT send 'categorySlugs' (API ignores it, wastes bandwidth)
- Fetch 10+ pages to get comprehensive results (30 per page max)
- Client-side filter by: time_range (via activationTime.passedDays), level (via seniorityLevel)
"""
import requests
import time
import logging

logger = logging.getLogger(__name__)

LIST_API = "https://candidateapi.jobvision.ir/api/v1/JobPost/List"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://jobvision.ir",
    "Referer": "https://jobvision.ir/",
}

PROVINCE_SLUGS = {
    'تهران': 'in-all-cities-of-tehran',
    'اصفهان': 'in-all-cities-of-isfahan',
    'البرز': 'in-all-cities-of-alborz',
    'خراسان رضوی': 'in-all-cities-of-khorasan-razavi',
    'فارس': 'in-all-cities-of-fars',
    'خوزستان': 'in-all-cities-of-khoozestan',
    'گیلان': 'in-all-cities-of-gilan',
    'مازندران': 'in-all-cities-of-mazandaran',
    'آذربایجان شرقی': 'in-all-cities-of-azarbayjan-sharghi',
    'آذربایجان غربی': 'in-all-cities-of-azarbayjan-gharbi',
    'کرمان': 'in-all-cities-of-kerman',
    'هرمزگان': 'in-all-cities-of-hormozgan',
    'یزد': 'in-all-cities-of-yazd',
    'مرکزی': 'in-all-cities-of-markazi',
    'گلستان': 'in-all-cities-of-golestan',
    'سمنان': 'in-all-cities-of-semnan',
    'کرمانشاه': 'in-all-cities-of-kermanshah',
    'همدان': 'in-all-cities-of-hamedan',
    'لرستان': 'in-all-cities-of-lorestan',
    'بوشهر': 'in-all-cities-of-booshehr',
    'زنجان': 'in-all-cities-of-zanjan',
    'اردبیل': 'in-all-cities-of-ardabil',
    'چهارمحال و بختیاری': 'in-all-cities-of-chaharmahal-&-bakhtiari',
    'سیستان و بلوچستان': 'in-all-cities-of-sistan-&-baluchestan',
    'کردستان': 'in-all-cities-of-koodestan',
    'ایلام': 'in-all-cities-of-ilam',
    'خراسان شمالی': 'in-all-cities-of-khorasan-shomali',
    'خراسان جنوبی': 'in-all-cities-of-khorasan-jonoobi',
    'کهگیلویه و بویراحمد': 'in-all-cities-of-kohgilooye-&-boyerahmad',
    'قزوین': 'in-all-cities-of-ghazvin',
    'قم': 'in-all-cities-of-ghom',
}

API_TIMEOUT = 25


def _get_session():
    """Create a new requests Session for each call (thread-safe)."""
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _job_matches_level(job: dict, level: str) -> bool:
    """Check seniority level match using title-based matching."""
    if not level or level == 'all':
        return True
    seniority = job.get('seniorityLevel') or {}
    title_fa = (seniority.get('titleFa', '') or '').lower()
    title_en = (seniority.get('titleEn', '') or '').lower()
    title = f"{title_fa} {title_en}"
    if not title.strip():
        return True
    lm = {
        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'کارآموزی', 'junior', 'intern', 'trainee', 'entry'],
        'mid': ['کارشناس', 'متخصص', 'میان‌رده', 'mid', 'intermediate'],
        'senior': ['ارشد', 'سنیور', 'senior', 'lead', 'expert', 'principal', 'کارشناس ارشد', 'تخصص بالا'],
        'manager': ['مدیر', 'manager', 'director', 'head', 'vp', 'مدیریتی', 'سرپرست', 'رئیس', 'معاون'],
    }
    criteria = lm.get(level, [])
    if not criteria:
        return True
    return any(c in title for c in criteria)


def _job_matches_time(job: dict, time_range: str) -> bool:
    """Client-side time filtering using activationTime.passedDays.
    
    The API IGNORES publishedDateGte, so we filter here.
    """
    if not time_range or time_range == 'all':
        return True
    try:
        max_days = int(time_range)
    except (ValueError, TypeError):
        return True
    
    act = job.get('activationTime') or {}
    passed_days = act.get('passedDays')
    if passed_days is None:
        return True  # Can't filter without data
    return passed_days <= max_days


def crawl_jobvision(keywords: str = '', city: str = '', level: str = 'all',
                    time_range: str = '7', max_pages: int = 3,
                    category_slugs: list = None,
                    client_filter_keywords: list = None) -> list:
    """
    Crawl Jobvision via REST API.
    
    KEY: 'keyword' at top-level is the ONLY working search parameter.
    categorySlugs is IGNORED by the API.
    Time filtering is done client-side via activationTime.passedDays.
    Max 30 results per page — fetch many pages for comprehensive results.
    """
    results = []
    seen_ids = set()
    
    # Clean keyword (top-level, NOT inside filters)
    clean_kw = ' '.join(keywords.strip().split()[:5]) if keywords and keywords.strip() else ''
    
    # Build filters dict — only location works
    filters = {}
    if city and city in PROVINCE_SLUGS:
        filters['locationSlugs'] = [PROVINCE_SLUGS[city]]
    
    logger.info(f"Jobvision: keyword='{clean_kw[:60]}', city={city}, time_range={time_range}")
    
    # Fetch many pages — API returns max 30 per page
    # For 3 "requested" pages, fetch 10 actual pages (300 potential results)
    effective_pages = max(max_pages * 3, 10)
    
    for page in range(1, effective_pages + 1):
        try:
            payload = {
                "page": page,
                "pageSize": 40,  # API caps at 30 anyway
                "sort": 1,
                "filters": filters,
            }
            # keyword goes at TOP-LEVEL (the only working search param)
            if clean_kw:
                payload['keyword'] = clean_kw
            
            _s = _get_session()
            resp = _s.post(LIST_API, json=payload, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get('isSuccess'):
                logger.warning(f"Jobvision API error: {data.get('message', 'unknown')}")
                break
            
            job_posts = data.get('data', {}).get('jobPosts', [])
            total_count = data.get('data', {}).get('jobPostCount', 0)
            if page == 1:
                logger.info(f"Jobvision: {total_count} total jobs for keyword='{clean_kw[:30]}'")
            
            if not job_posts:
                logger.info(f"Jobvision: no more jobs at page {page}")
                break
            
            page_matches = 0
            for job in job_posts:
                jid = job.get('id')
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)
                
                # --- Client-side time filtering ---
                if not _job_matches_time(job, time_range):
                    continue
                
                # --- Client-side level filtering ---
                if not _job_matches_level(job, level):
                    continue
                
                page_matches += 1
                
                # --- Extract all data ---
                title = job.get('title', '')
                
                company_info = job.get('company', {}) or {}
                company = (company_info.get('nameFa', '') or
                          company_info.get('nameEn', '') or '')
                
                loc = job.get('location', {}) or {}
                city_obj = loc.get('city', {}) or {}
                prov_obj = loc.get('province', {}) or {}
                city_name = (city_obj.get('titleFa', '') or
                            city_obj.get('name', '') or
                            prov_obj.get('titleFa', ''))
                province_name = prov_obj.get('titleFa', '') or prov_obj.get('name', '')
                
                sal = job.get('salary', {}) or {}
                salary = sal.get('titleFa', '')
                if not salary:
                    mn = sal.get('min', '')
                    mx = sal.get('max', '')
                    if mn or mx:
                        salary = f"{mn or ''} - {mx or ''} میلیون تومان"
                
                wt = job.get('workType', {}) or {}
                work_type = wt.get('titleFa', '') or wt.get('titleEn', '')
                
                sr = job.get('seniorityLevel', {}) or {}
                seniority = sr.get('titleFa', '') or sr.get('titleEn', '')
                
                skills = []
                for s in (job.get('skills') or []):
                    if isinstance(s, dict):
                        skills.append(s.get('titleFa', '') or s.get('titleEn', ''))
                    elif isinstance(s, str):
                        skills.append(s)
                
                cats = []
                for c in (job.get('jobCategories') or []):
                    n = c.get('titleFa', '') or c.get('titleEn', '')
                    if n:
                        cats.append(n)
                
                props = job.get('properties', {}) or {}
                is_remote = props.get('isRemote', False)
                
                act = job.get('activationTime', {}) or {}
                posted_date = act.get('beautifyFa', '') or ''
                
                benefits = []
                for b in (job.get('benefits', []) or []):
                    if isinstance(b, dict):
                        benefits.append(b.get('titleFa', '') or b.get('titleEn', ''))
                    elif isinstance(b, str):
                        benefits.append(b)
                
                url = f"https://jobvision.ir/jobs/{jid}"
                
                desc_parts = []
                if cats:
                    desc_parts.append(f"دسته: {', '.join(cats[:3])}")
                if benefits:
                    desc_parts.append(f"مزایا: {', '.join(benefits[:5])}")
                description = ' | '.join(desc_parts)
                
                all_skills = skills + benefits
                
                results.append({
                    'platform': 'jobvision',
                    'title': title,
                    'company': company,
                    'city': city_name,
                    'province': province_name,
                    'salary': salary,
                    'job_type': work_type,
                    'seniority_level': seniority,
                    'description': description,
                    'skills': all_skills,
                    'url': url,
                    'remote': is_remote,
                    'posted_date': posted_date,
                })
            
            logger.info(f"Jobvision page {page}: {len(job_posts)} API, "
                        f"{page_matches} matched (total: {len(results)})")
            time.sleep(0.3)
            
            # Stop if we have enough results
            if len(results) >= max_pages * 40:
                break
            
        except requests.Timeout:
            logger.error(f"Jobvision timeout at page {page}")
            break
        except requests.ConnectionError as e:
            logger.error(f"Jobvision connection error: {e}")
            break
        except Exception as e:
            logger.error(f"Jobvision error at page {page}: {e}")
            break
    
    logger.info(f"Jobvision total: {len(results)} jobs")
    return results
