import requests
import time
import logging

logger = logging.getLogger(__name__)

LIST_API = "https://candidateapi.jobvision.ir/api/v1/JobPost/List"
DETAIL_API = "https://candidateapi.jobvision.ir/api/v1/JobPost/Detail"
FILTERS_API = "https://candidateapi.jobvision.ir/api/v1/JobPost/GetAllSearchFilters"

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

CATEGORY_SLUGS = {
    'برنامه‌نویسی و توسعه نرم‌افزار': 'developer',
    'علم داده و هوش مصنوعی': 'data-science',
    'طراحی گرافیک و UI/UX': 'ui-ux',
    'بازاریابی و فروش': 'digital-marketing',
    'مالی و حسابداری': 'accounting',
    'منابع انسانی': 'human-resources',
    'مدیریت و رهبری': 'business-development',
    'شبکه و زیرساخت': 'network',
    'امنیت سایبری': 'network',
    'DevOps و زیرساخت': 'developer',
    'تولید محتوا و کپی‌رایتینگ': 'content',
}

# Timeouts
API_TIMEOUT = 20   # seconds per API call
DETAIL_TIMEOUT = 15  # seconds per detail fetch

session = requests.Session()
session.headers.update(HEADERS)


def crawl_jobvision(keywords: str, city: str = '', level: str = 'all',
                    time_range: str = '7', max_pages: int = 3) -> list:
    """
    Crawl Jobvision for job listings.
    Returns list of dicts with job data.
    """
    results = []
    seen_ids = set()

    # Build filters
    filters = {}
    if keywords.strip():
        filters['keyword'] = keywords.strip()

    if city and city in PROVINCE_SLUGS:
        filters['locationSlugs'] = [PROVINCE_SLUGS[city]]

    if level != 'all' and level in LEVEL_MAP:
        filters['seniorityLevelIds'] = [LEVEL_MAP[level]]

    logger.info(f"Jobvision: searching keywords='{keywords.strip()[:50]}', city={city}, level={level}")

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
                logger.warning(f"Jobvision API error: {data}")
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

                # Extract data from list
                title_info = job.get('title', {})
                title = title_info.get('titleFa', '') or title_info.get('titleEn', '')

                company_info = job.get('company', {})
                company = company_info.get('name', '')

                location_info = job.get('location', {})
                city_name = (location_info.get('city', {}) or {}).get('name', '')
                province_name = (location_info.get('province', {}) or {}).get('name', '')

                salary_info = job.get('salary', {})
                salary = ''
                if salary_info:
                    min_s = salary_info.get('minSalary', 0)
                    max_s = salary_info.get('maxSalary', 0)
                    if min_s or max_s:
                        salary = f"{min_s or ''} - {max_s or ''} تومان"
                    c = salary_info.get('currencyTitleFa', '')
                    if c:
                        salary = f"{salary} {c}".strip()

                work_type_info = job.get('workType', {})
                work_type = (work_type_info.get('titleFa', '') or
                             work_type_info.get('titleEn', ''))

                seniority_info = job.get('seniorityLevel', {})
                seniority = (seniority_info.get('titleFa', '') or
                             seniority_info.get('titleEn', ''))

                skills = [s.get('titleFa', '') or s.get('titleEn', '')
                          for s in job.get('skills', []) if s]

                is_remote = job.get('isRemote', False)

                # Get detail for description (with timeout protection)
                description = ''
                posted_date = ''
                try:
                    time.sleep(0.3)
                    detail_resp = session.get(
                        DETAIL_API,
                        params={"jobPostId": job_id},
                        timeout=DETAIL_TIMEOUT
                    )
                    if detail_resp.ok:
                        detail_data = detail_resp.json()
                        if detail_data.get('isSuccess'):
                            d = detail_data['data']
                            description = d.get('description', '')
                            posted_date = d.get('publishedAtPersian', '')
                except requests.Timeout:
                    logger.debug(f"Detail fetch timeout for job {job_id}")
                except Exception as e:
                    logger.debug(f"Detail fetch error for {job_id}: {e}")

                # Apply time range filter
                if time_range != 'all' and posted_date:
                    pass  # future: parse Persian date

                url = f"https://jobvision.ir/jobs/{job_id}"

                results.append({
                    'platform': 'jobvision',
                    'title': title,
                    'company': company,
                    'city': city_name or province_name,
                    'province': province_name,
                    'salary': salary,
                    'job_type': work_type,
                    'seniority_level': seniority,
                    'description': description,
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