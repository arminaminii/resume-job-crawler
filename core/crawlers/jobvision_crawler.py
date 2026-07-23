"""
JobVision crawler — uses their PUBLIC REST API.

API endpoint: POST https://candidateapi.jobvision.ir/api/v1/JobPost/List

RESEARCH FINDINGS (tested 2026-07-23 from crawl-py repo + direct API testing):
1. 'keyword' at TOP-LEVEL is the ONLY working search param (654 for 'python')
   'filters.keyword' is IGNORED (43,688 = all jobs). Persian keywords don't work.
2. 'sort': 0 = newest first (confirmed by crawl-py reference implementation)
3. 'publishedDateGte' is IGNORED — use client-side 'activationTime.passedDays'
4. Maximum 30 results per page regardless of pageSize
5. 'locationSlugs' in filters WORKS for province filtering
6. 'categorySlugs' is IGNORED

REFERENCE: https://github.com/mahdi-esmaeelnezhad/crawl-py/blob/main/jobvision_crawler.py
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

API_TIMEOUT = 30


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
    if not seniority:
        return True  # If no seniority data, don't filter out
    title_fa = (seniority.get('titleFa', '') or '').lower()
    title_en = (seniority.get('titleEn', '') or '').lower()
    title = f"{title_fa} {title_en}"
    if not title.strip():
        return True
    lm = {
        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'کارآموزی', 'junior', 'intern',
                    'trainee', 'entry', 'کارآموزی'],
        'mid': ['کارشناس', 'متخصص', 'میان‌رده', 'mid', 'intermediate',
                'کارشناس ارشد / متخصص', 'junior professional'],
        'senior': ['ارشد', 'سنیور', 'senior', 'lead', 'expert', 'principal',
                   'کارشناس ارشد', 'تخصص بالا', 'تخصص بالا'],
        'manager': ['مدیر', 'manager', 'director', 'head', 'vp', 'مدیریتی',
                   'سرپرست', 'رئیس', 'معاون'],
    }
    criteria = lm.get(level, [])
    if not criteria:
        return True
    return any(c in title for c in criteria)


def _job_matches_time(job: dict, time_range: str) -> bool:
    """Client-side time filtering using activationTime.passedDays."""
    if not time_range or time_range == 'all':
        return True
    try:
        max_days = int(time_range)
    except (ValueError, TypeError):
        return True
    
    act = job.get('activationTime') or {}
    passed_days = act.get('passedDays')
    if passed_days is None:
        return True
    return passed_days <= max_days


def _text_fa(value):
    """Extract Farsi text from a JobVision API field (dict or str)."""
    if value is None:
        return ''
    if isinstance(value, dict):
        return (value.get('titleFa', '') or value.get('title', '') or
                value.get('titleEn', '') or value.get('beautifyFa', '') or '')
    return str(value).strip()


def crawl_jobvision(keywords: str = '', city: str = '', level: str = 'all',
                    time_range: str = '7', max_pages: int = 3,
                    category_slugs: list = None,
                    client_filter_keywords: list = None) -> list:
    """
    Crawl Jobvision via REST API.
    
    Search with keyword at TOP-LEVEL (the only working approach).
    'filters' is only for locationSlugs.
    
    Time filtering: client-side via activationTime.passedDays
    Max 30 results per page — fetch many pages.
    """
    results = []
    seen_ids = set()
    
    # Clean keyword
    clean_kw = ' '.join(keywords.strip().split()[:5]) if keywords and keywords.strip() else ''
    
    # Build filters dict — location only
    filters = {}
    if city and city in PROVINCE_SLUGS:
        filters['locationSlugs'] = [PROVINCE_SLUGS[city]]
    
    logger.info(f"Jobvision: keyword='{clean_kw[:60]}', city={city}, time_range={time_range}")
    
    effective_pages = max(max_pages * 3, 10)
    
    for page in range(1, effective_pages + 1):
        try:
            payload = {
                "page": page,
                "pageSize": 30,
                "sort": 0,
                "filters": filters,
            }
            # keyword at TOP-LEVEL
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
                break
            
            page_matches = 0
            for job in job_posts:
                jid = job.get('id')
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)
                
                # Client-side time filtering
                if not _job_matches_time(job, time_range):
                    continue
                
                # Client-side level filtering (pass if no data)
                if not _job_matches_level(job, level):
                    continue
                
                page_matches += 1
                
                # Extract all data
                title = job.get('title', '')
                
                company_info = job.get('company', {}) or {}
                company = (company_info.get('nameFa', '') or
                          company_info.get('nameEn', '') or '')
                
                loc = job.get('location', {}) or {}
                city_obj = loc.get('city', {}) or {}
                prov_obj = loc.get('province', {}) or {}
                city_name = _text_fa(city_obj) or _text_fa(prov_obj)
                province_name = _text_fa(prov_obj)
                
                sal = job.get('salary', {}) or {}
                salary = _text_fa(sal)
                
                work_type = _text_fa(job.get('workType'))
                seniority = _text_fa(job.get('seniorityLevel'))
                
                # Skills (from skills array)
                skills = [_text_fa(s) for s in (job.get('skills') or []) if _text_fa(s)]
                
                # Job categories
                cats = [_text_fa(c) for c in (job.get('jobCategories') or []) if _text_fa(c)]
                
                # Benefits
                benefits = [_text_fa(b) for b in (job.get('benefits') or []) if _text_fa(b)]
                
                props = job.get('properties', {}) or {}
                is_remote = props.get('isRemote', False)
                
                act = job.get('activationTime', {}) or {}
                posted_date = _text_fa(act) or act.get('beautifyFa', '')
                
                url = f"https://jobvision.ir/jobs/{jid}"
                
                desc_parts = []
                if cats:
                    desc_parts.append('دسته: ' + ', '.join(cats[:3]))
                if benefits:
                    desc_parts.append('مزایا: ' + ', '.join(benefits[:5]))
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
            
            if len(results) >= max_pages * 50:
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
