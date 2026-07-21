"""
E-estekhdam crawler — uses their PUBLIC REST API (no Playwright needed).

API endpoint: POST https://www.e-estekhdam.com/search-api/search?page=N
Returns JSON array of job objects with structured data.

No authentication required. Pagination via ?page=N (20 items per page).
"""
import requests
import logging
import re
import time

logger = logging.getLogger(__name__)

BASE_URL = "https://www.e-estekhdam.com"
SEARCH_API = f"{BASE_URL}/search-api/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/search/",
}

# Province name to E-estekhdam API label
PROVINCE_MAP = {
    'تهران': 'تهران', 'اصفهان': 'اصفهان', 'البرز': 'البرز',
    'خراسان رضوی': 'خراسان رضوی', 'فارس': 'فارس', 'خوزستان': 'خوزستان',
    'گیلان': 'گیلان', 'مازندران': 'مازندران', 'آذربایجان شرقی': 'آذربایجان شرقی',
    'آذربایجان غربی': 'آذربایجان غربی', 'کرمان': 'کرمان', 'هرمزگان': 'هرمزگان',
    'یزد': 'یزد', 'مرکزی': 'اراک', 'گلستان': 'گلستان', 'سمنان': 'سمنان',
    'کرمانشاه': 'کرمانشاه', 'همدان': 'همدان', 'لرستان': 'لرستان',
    'بوشهر': 'بوشهر', 'زنجان': 'زنجان', 'اردبیل': 'اردبیل',
    'چهارمحال و بختیاری': 'چهار محال', 'سیستان و بلوچستان': 'سیستان و بلوچستان',
    'کردستان': 'کردستان', 'ایلام': 'ایلام', 'خراسان شمالی': 'خراسان شمالی',
    'خراسان جنوبی': 'خراسان جنوبی', 'کهگیلویه و بویراحمد': 'کهگیلویه و بویراحمد',
    'قزوین': 'قزوین', 'قم': 'قم', 'سرداب': 'سرداب', 'خوزستان': 'خوزستان',
}

# Benefit key to Persian label
BENEFIT_LABELS = {
    'insurance': 'بیمه',
    'supplementary_insurance': 'بیمه تکمیلی',
    'reward': 'پاداش',
    'loan': 'وام',
    'commission': 'کمیسیون',
    'commuting_service': 'سرویس ایاب و ذهاب',
    'gift': 'هدیه',
    'breakfast': 'صبحانه',
    'launch': 'ناهار',
    'snack': 'میان‌وعده',
    'remote_work': 'دورکاری',
    'flexible_hours': 'ساعت کاری منعطف',
    'training_allowance': 'حق‌الآموزش',
    'buy_coupon': 'بن خرید',
    'tourism_facility': 'تسهیلات گردشگری',
    'incentive_stock': 'سهام تشویقی',
}

API_TIMEOUT = 20

session = requests.Session()
session.headers.update(HEADERS)


def crawl_estekhdam(keywords: str = '', city: str = '', level: str = 'all',
                     time_range: str = '7', max_pages: int = 2) -> list:
    """
    Crawl e-estekhdam.com via their public REST API.
    No Playwright or browser needed — fast and reliable.

    Returns list of dicts with normalized job data.
    """
    results = []
    seen_ids = set()

    # Build request body (most filters don't work server-side,
    # but we include them anyway in case they add support)
    body = {}

    # Try to set province filter
    if city and city in PROVINCE_MAP:
        body['where'] = PROVINCE_MAP[city]

    # Build keyword list for client-side filtering
    search_terms = []
    if keywords and keywords.strip():
        search_terms = [kw.strip().lower() for kw in keywords.split() if kw.strip()]

    logger.info(f"E-estekhdam: searching keywords='{keywords.strip()[:50]}', "
                f"city={city}, body={body}")

    for page in range(1, max_pages + 1):
        try:
            resp = session.post(
                f"{SEARCH_API}?page={page}",
                json=body,
                timeout=API_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()

            if not data.get('ok'):
                logger.warning(f"E-estekhdam API error: {data.get('status')}")
                break

            jobs = data.get('data', [])
            if not jobs:
                logger.info(f"E-estekhdam: no more jobs at page {page}")
                break

            for job in jobs:
                job_id = job.get('id')
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                title = job.get('title', '') or job.get('short_title', '')
                company = job.get('brand_name', '')
                provinces = job.get('provinces', []) or []
                province_name = ', '.join(provinces) if provinces else ''
                location = job.get('location', '') or ''
                city_name = location.split('،')[-1].strip() if location else (province_name or '')

                # Contract / job type
                contracts = job.get('contract', []) or []
                job_type = ', '.join(contracts) if contracts else ''

                # Salary
                salary = job.get('salary', '') or ''

                # Benefits
                benefits_raw = job.get('benefits', []) or []
                benefits = [BENEFIT_LABELS.get(b, b) for b in benefits_raw]

                # Technologies / skills
                technologies = job.get('technologies', []) or []

                # Remote detection
                is_remote = any(
                    kw in job_type for kw in ['دورکاری', 'Remote']
                ) or 'remote_work' in (benefits_raw or [])

                # URL
                url_path = job.get('url', '')
                url = f"{BASE_URL}{url_path}" if url_path else ''

                # Is new (posted recently)
                is_new = job.get('is_new', False)
                is_promoted = job.get('promoted', False)

                # Seniority level
                position_levels = job.get('position_levels') or []
                seniority = ', '.join(position_levels) if position_levels else ''

                # Build description from available data
                desc_parts = []
                if job.get('brand_sector'):
                    desc_parts.append(f"حوزه: {job['brand_sector']}")
                if benefits:
                    desc_parts.append(f"مزایا: {', '.join(benefits)}")
                if technologies:
                    desc_parts.append(f"تکنولوژی‌ها: {', '.join(technologies)}")
                description = ' | '.join(desc_parts)

                # Client-side keyword filtering
                if search_terms:
                    title_lower = title.lower()
                    desc_lower = description.lower()
                    company_lower = company.lower()
                    combined = f"{title_lower} {desc_lower} {company_lower}"
                    # At least one search term must match
                    if not any(term in combined for term in search_terms):
                        continue

                # Level filtering
                if level != 'all':
                    level_map = {
                        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'مقدماتی', 'مردود'],
                        'mid': ['متوسط', 'میان‌رده'],
                        'senior': ['ارشد', 'سنیور', 'Senior', 'مدیر'],
                        'manager': ['مدیر', 'Manager', 'سرپرست'],
                    }
                    level_kw = level_map.get(level, [])
                    if level_kw:
                        full_text = f"{title} {description} {job_type} {seniority}"
                        if not any(kw in full_text for kw in level_kw):
                            continue

                results.append({
                    'platform': 'e_estekhdam',
                    'title': title,
                    'company': company,
                    'city': city_name,
                    'province': province_name,
                    'salary': salary,
                    'job_type': job_type,
                    'seniority_level': seniority,
                    'description': description,
                    'skills': technologies + benefits,
                    'url': url,
                    'remote': is_remote,
                    'posted_date': 'جدید' if is_new else '',
                })

            logger.info(f"E-estekhdam page {page}: got {len(jobs)} jobs "
                        f"(total so far: {len(results)})")
            time.sleep(0.3)

        except requests.Timeout:
            logger.error(f"E-estekhdam API timeout at page {page}")
            break
        except requests.ConnectionError as e:
            logger.error(f"E-estekhdam connection error: {e}")
            break
        except Exception as e:
            logger.error(f"E-estekhdam error at page {page}: {e}")
            break

    logger.info(f"E-estekhdam total: {len(results)} jobs")
    return results
