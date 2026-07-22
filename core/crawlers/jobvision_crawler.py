"""
Jobvision crawler — uses their REST API.

API endpoint: POST https://candidateapi.jobvision.ir/api/v1/JobPost/List
Returns JSON with jobPosts array.

KEY DESIGN DECISIONS:
1. categorySlugs is sent for server-side category filtering
2. keyword is sent ONLY from user input (not category-derived)
   This avoids AND filter between keyword+categorySlugs
3. client_filter_keywords provides CLIENT-SIDE filtering as safety net
4. pageSize=40 and more pages to get comprehensive results
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

# NOTE: API ignores seniorityLevelIds in filters — only title-based client filter works.
# Actual API seniority IDs vary (e.g. 97=کارشناس, 172=کارشناس ارشد), not 2-5.

API_TIMEOUT = 25

def _get_session():
    """Create a new requests Session for each call (thread-safe)."""
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _job_matches_client_filter(job: dict, client_kws: list) -> bool:
    """Client-side OR filter: at least one keyword from category must match."""
    if not client_kws:
        return True
    parts = [job.get('title', '')]
    co = job.get('company') or {}
    parts.append(co.get('nameFa', '') or co.get('nameEn', '') or '')
    for s in (job.get('skills') or []):
        if isinstance(s, dict):
            parts.append(s.get('titleFa', '') or s.get('titleEn', ''))
        elif isinstance(s, str):
            parts.append(s)
    for c in (job.get('jobCategories') or []):
        parts.append(c.get('titleFa', '') or c.get('titleEn', ''))
    desc = job.get('description', '') or ''
    if desc:
        parts.append(desc)
    full_text = ' '.join(parts).lower()
    return any(kw.lower() in full_text for kw in client_kws)


def _job_matches_level(job: dict, level: str) -> bool:
    """Check seniority level match using TITLE-based matching only.
    
    The API ignores seniorityLevelIds in filters, so we filter client-side.
    Actual seniority titles from API: کارآموز, کارشناس, کارشناس ارشد, مدیر, etc.
    """
    if not level or level == 'all':
        return True
    seniority = job.get('seniorityLevel') or {}
    title_fa = (seniority.get('titleFa', '') or '').lower()
    title_en = (seniority.get('titleEn', '') or '').lower()
    title = f"{title_fa} {title_en}"
    if not title.strip():
        return True  # Can't filter without data
    lm = {
        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'کارآموزی', 'junior', 'intern', 'trainee', 'entry'],
        'mid': ['کارشناس', 'متخصص', 'میان‌رده', 'mid', 'intermediate'],
        'senior': ['ارشد', 'سنیور', 'senior', 'lead', 'expert', 'principal', 'کارشناس ارشد', 'تخصص بالا'],
        'manager': ['مدیر', 'manager', 'director', 'head', 'vp', 'مدیریتی', 'سرپرست', 'رئیس'],
    }
    criteria = lm.get(level, [])
    if not criteria:
        return True
    return any(c in title for c in criteria)


def crawl_jobvision(keywords: str = '', city: str = '', level: str = 'all',
                    time_range: str = '7', max_pages: int = 3,
                    category_slugs: list = None,
                    client_filter_keywords: list = None) -> list:
    """
    Crawl Jobvision via REST API.
    - category_slugs: sent to API for server-side filtering
    - client_filter_keywords: used ONLY for client-side filtering (safety net)
    - keywords: user's explicit search terms (sent to API)
    """
    results = []
    seen_ids = set()
    cfk = client_filter_keywords or []

    # --- Build API payload ---
    # CRITICAL: keyword MUST be top-level, NOT inside filters!
    # The API ignores keyword inside filters.
    clean_kw = ' '.join(keywords.strip().split()[:5]) if keywords and keywords.strip() else ''

    filters = {}

    # Category slugs — server-side filtering
    if category_slugs:
        unique = list(set(s for s in category_slugs if s))
        if unique:
            filters['categorySlugs'] = unique
            logger.info(f"Jobvision API: categorySlugs={unique}")

    if city and city in PROVINCE_SLUGS:
        filters['locationSlugs'] = [PROVINCE_SLUGS[city]]

    # Note: API ignores seniorityLevelIds — level filtering done client-side only

    if time_range and time_range != 'all':
        try:
            from datetime import datetime, timedelta
            days = int(time_range)
            cutoff = datetime.now() - timedelta(days=days)
            filters['publishedDateGte'] = int(cutoff.timestamp() * 1000)
        except (ValueError, TypeError):
            pass

    logger.info(f"Jobvision: keyword='{clean_kw[:50]}', city={city}, "
                f"categories={filters.get('categorySlugs', [])}, "
                f"client_filter_kws={len(cfk)}")

    # Fetch extra pages for client-side filtering safety net
    effective_pages = max_pages + 2

    for page in range(1, effective_pages + 1):
        try:
            payload = {
                "page": page,
                "pageSize": 40,
                "sort": 1,
                "filters": filters,
            }
            # keyword goes at TOP-LEVEL, not inside filters
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
                logger.info(f"Jobvision: {total_count} total jobs on platform")

            if not job_posts:
                logger.info(f"Jobvision: no more jobs at page {page}")
                break

            page_matches = 0
            for job in job_posts:
                jid = job.get('id')
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)

                # Client-side filtering
                if not _job_matches_client_filter(job, cfk):
                    continue
                if not _job_matches_level(job, level):
                    continue

                page_matches += 1

                # --- Extract all data from API response ---
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

                if len(results) >= max_pages * 40:
                    break

            logger.info(f"Jobvision page {page}: {len(job_posts)} API, "
                        f"{page_matches} matched (total: {len(results)})")
            time.sleep(0.4)

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