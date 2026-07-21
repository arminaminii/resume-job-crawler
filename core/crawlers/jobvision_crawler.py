import requests
import time
import logging

logger = logging.getLogger(__name__)

LIST_API = "https://candidateapi.jobvision.ir/api/v1/JobPost/List"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://jobvision.ir",
    "Referer": "https://jobvision.ir/",
}

# Province slug mapping
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

LEVEL_MAP = {
    'junior': 2,   # کارآموز / جونیور
    'mid': 3,      # متوسط
    'senior': 4,   # ارشد / سنیور
    'manager': 5,  # مدیریتی
    'all': 0,
}

# Timeout
API_TIMEOUT = 20   # seconds per API call

session = requests.Session()
session.headers.update(HEADERS)


def crawl_jobvision(keywords: str, city: str = '', level: str = 'all',
                    time_range: str = '7', max_pages: int = 2,
                    category_slugs: list = None) -> list:
    """
    Crawl Jobvision for job listings via REST API.
    Returns list of dicts with job data.
    category_slugs: list of Jobvision category slugs from JobCategory.jobvision_slug
    """
    results = []
    seen_ids = set()

    # Build filters
    filters = {}
    # Truncate keywords to prevent API issues (max ~200 chars)
    clean_keywords = ' '.join(keywords.strip().split()[:10]) if keywords.strip() else ''
    if clean_keywords:
        filters['keyword'] = clean_keywords

    # Use category slugs for Jobvision's categorySlug filter
    if category_slugs:
        unique_slugs = list(set(s for s in category_slugs if s))
        if unique_slugs:
            filters['categorySlugs'] = unique_slugs

    if city and city in PROVINCE_SLUGS:
        filters['locationSlugs'] = [PROVINCE_SLUGS[city]]

    if level != 'all' and level in LEVEL_MAP:
        filters['seniorityLevelIds'] = [LEVEL_MAP[level]]

    # Time range filter (days ago)
    if time_range and time_range != 'all':
        try:
            from datetime import datetime, timedelta
            days = int(time_range)
            cutoff = datetime.now() - timedelta(days=days)
            # Jobvision expects Unix timestamp in milliseconds
            filters['publishedDateGte'] = int(cutoff.timestamp() * 1000)
        except (ValueError, TypeError):
            pass

    logger.info(f"Jobvision: searching keywords='{keywords.strip()[:50]}', "
                f"city={city}, level={level}, categories={category_slugs}, "
                f"time_range={time_range}, filters={list(filters.keys())}")

    for page in range(1, max_pages + 1):
        try:
            payload = {
                "page": page,
                "pageSize": 20,
                "sort": 0,
                "filters": filters,
            }
            resp = session.post(LIST_API, json=payload, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if not data.get('isSuccess'):
                logger.warning(f"Jobvision API error: {data.get('message', 'unknown')}")
                break

            job_posts = data.get('data', {}).get('jobPosts', [])
            if not job_posts:
                logger.info(f"Jobvision: no more jobs at page {page}")
                break

            for job in job_posts:
                job_id = job.get('id')
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                # Title is a DIRECT STRING (not an object)
                title = job.get('title', '')

                # Company info
                company_info = job.get('company', {}) or {}
                company = company_info.get('nameFa', '') or company_info.get('nameEn', '')

                # Location info - city and province are nested objects
                location_info = job.get('location', {}) or {}
                city_obj = (location_info.get('city', {}) or {})
                province_obj = (location_info.get('province', {}) or {})
                city_name = (city_obj.get('titleFa', '') or
                              city_obj.get('name', '') or
                              province_obj.get('titleFa', ''))

                # Salary info
                salary_info = job.get('salary', {}) or {}
                salary = salary_info.get('titleFa', '')
                if not salary:
                    min_s = salary_info.get('min', '')
                    max_s = salary_info.get('max', '')
                    if min_s or max_s:
                        salary = f"{min_s or ''} - {max_s or ''} میلیون تومان"

                # Work type
                work_type_info = job.get('workType', {}) or {}
                work_type = work_type_info.get('titleFa', '') or work_type_info.get('titleEn', '')

                # Seniority level
                seniority_info = job.get('seniorityLevel', {}) or {}
                seniority = seniority_info.get('titleFa', '') or seniority_info.get('titleEn', '')

                # Skills
                skills_raw = job.get('skills', []) or []
                skills = []
                for s in skills_raw:
                    if isinstance(s, dict):
                        skills.append(s.get('titleFa', '') or s.get('titleEn', ''))
                    elif isinstance(s, str):
                        skills.append(s)

                # Remote status
                properties = job.get('properties', {}) or {}
                is_remote = properties.get('isRemote', False)

                # Posted date
                activation = job.get('activationTime', {}) or {}
                posted_date = activation.get('beautifyFa', '') or ''

                # Province name for display
                province_name = province_obj.get('titleFa', '') or province_obj.get('name', '')

                url = f"https://jobvision.ir/jobs/{job_id}"

                results.append({
                    'platform': 'jobvision',
                    'title': title,
                    'company': company,
                    'city': city_name,
                    'province': province_name,
                    'salary': salary,
                    'job_type': work_type,
                    'seniority_level': seniority,
                    'description': '',
                    'skills': skills,
                    'url': url,
                    'remote': is_remote,
                    'posted_date': posted_date,
                })

            logger.info(f"Jobvision page {page}: got {len(job_posts)} jobs (total so far: {len(results)})")
            time.sleep(0.5)

        except requests.Timeout:
            logger.error(f"Jobvision API timeout at page {page}")
            break
        except requests.ConnectionError as e:
            logger.error(f"Jobvision connection error at page {page}: {e}")
            break
        except requests.RequestException as e:
            logger.error(f"Jobvision crawl error page {page}: {e}")
            break
        except Exception as e:
            logger.error(f"Jobvision unexpected error page {page}: {e}")
            break

    logger.info(f"Jobvision total: {len(results)} jobs")
    return results