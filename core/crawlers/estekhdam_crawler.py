"""
E-estekhdam crawler — uses their PUBLIC REST API.

API endpoint: POST https://www.e-estekhdam.com/search-api/search?page=N
Returns JSON with {ok: true, data: [...]} structure.

FIXES APPLIED:
1. Now sends 'title' keyword to the API body for server-side filtering
2. Uses client_filter_keywords for client-side category matching
3. Increased page size and better error handling
"""
import requests
import logging
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

PROVINCE_MAP = {
    'تهران': 'تهران', 'اصفهان': 'اصفهان', 'البرز': 'البرز',
    'خراسان رضوی': 'خراسان رضوی', 'فارس': 'فارس', 'خوزستان': 'خوزستان',
    'گیلان': 'گیلان', 'مازندران': 'مازندران', 'آذربایجان شرقی': 'آذربایجان شرقی',
    'آذربایجان غربی': 'آذربایجان غربی', 'کرمان': 'کرمان', 'هرمزگان': 'هرمزگان',
    'یزد': 'یزد', 'مرکزی': 'اراک', 'گلستان': 'گلستان', 'سمنان': 'سمنان',
    'کرمانشاه': 'کرمانشاه', 'همدان': 'همدان', 'لرستان': 'لرستان',
    'بوشهر': 'بوشهر', 'زنجان': 'زنجان', 'اردبیل': 'اردبیل',
    'چهارمحال و بختیاری': 'چهار محال',
    'سیستان و بلوچستان': 'سیستان و بلوچستان',
    'کردستان': 'کردستان', 'ایلام': 'ایلام',
    'خراسان شمالی': 'خراسان شمالی', 'خراسان جنوبی': 'خراسان جنوبی',
    'کهگیلویه و بویراحمد': 'کهگیلویه و بویراحمد',
    'قزوین': 'قزوین', 'قم': 'قم',
}

BENEFIT_LABELS = {
    'insurance': 'بیمه', 'supplementary_insurance': 'بیمه تکمیلی',
    'reward': 'پاداش', 'loan': 'وام', 'commission': 'کمیسیون',
    'commuting_service': 'سرویس ایاب و ذهاب', 'gift': 'هدیه',
    'breakfast': 'صبحانه', 'launch': 'ناهار', 'snack': 'میان‌وعده',
    'remote_work': 'دورکاری', 'flexible_hours': 'ساعت کاری منعطف',
    'training_allowance': 'حق‌الآموزش', 'buy_coupon': 'بن خرید',
    'tourism_facility': 'تسهیلات گردشگری', 'incentive_stock': 'سهام تشویقی',
}

API_TIMEOUT = 25

_session = requests.Session()
_session.headers.update(HEADERS)


def _job_matches_client_filter(job_data: dict, client_kws: list) -> bool:
    """Client-side OR filter using category keywords."""
    if not client_kws:
        return True
    combined = ' '.join([
        job_data.get('title', ''),
        job_data.get('company', ''),
        job_data.get('brand_sector', ''),
        ' '.join(job_data.get('technologies', [])),
        ' '.join(job_data.get('benefits', [])),
    ]).lower()
    return any(kw.lower() in combined for kw in client_kws)


def _job_matches_level(contracts: list, position_levels: list, level: str) -> bool:
    """Check seniority level match."""
    if not level or level == 'all':
        return True
    lm = {
        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'مقدماتی', 'مردود'],
        'mid': ['متوسط', 'میان‌رده'],
        'senior': ['ارشد', 'سنیور', 'Senior', 'مدیر'],
        'manager': ['مدیر', 'Manager', 'سرپرست'],
    }
    kws = lm.get(level, [])
    if not kws:
        return True
    full = ' '.join(contracts + position_levels)
    return any(kw in full for kw in kws)


def crawl_estekhdam(keywords: str = '', city: str = '', level: str = 'all',
                      time_range: str = '7', max_pages: int = 3,
                      category_slugs: list = None,
                      client_filter_keywords: list = None) -> list:
    """
    Crawl e-estekhdam.com via REST API.
    - keywords: user's search terms → sent to API as 'title'
    - category_slugs: E-estekhdam category names (sent to API if supported)
    - client_filter_keywords: category skills (client-side only)
    """
    results = []
    seen_ids = set()
    cfk = client_filter_keywords or []

    # Build POST body
    body = {}

    # Send keyword to API for server-side filtering
    # CRITICAL: The correct field is 'q', not 'title'
    if keywords and keywords.strip():
        kw_parts = [k.strip() for k in keywords.strip().split()[:3] if k.strip()]
        if kw_parts:
            body['q'] = ' '.join(kw_parts)
            logger.info(f"E-estekhdam API: searching q='{body['q']}'")

    if city and city in PROVINCE_MAP:
        body['where'] = PROVINCE_MAP[city]

    # Try sending category filter if available
    if category_slugs:
        for slug in category_slugs:
            if slug and slug not in body:
                body['category'] = slug
                break

    # IMPORTANT: E-estekhdam's API ignores search params and returns promoted jobs.
    # We always get ~20 promoted results regardless of query.
    # Client-side filtering is the ONLY way to get relevant results.
    # If we have keywords, they MUST be used for client-side filtering too.
    if keywords and keywords.strip():
        extra_kws = [k.strip().lower() for k in keywords.strip().split() if k.strip()]
        cfk = list(set((cfk or []) + extra_kws))

    logger.info(f"E-estekhdam: body={list(body.keys())}, city={city}")

    for page in range(1, max_pages + 1):
        try:
            resp = _session.post(
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
                logger.info(f"E-estekhdam: no more at page {page}")
                break

            for job in jobs:
                jid = job.get('id')
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)

                title = job.get('title', '') or job.get('short_title', '')
                company = job.get('brand_name', '')
                provinces = job.get('provinces', []) or []
                province_name = ', '.join(provinces) if provinces else ''
                location = job.get('location', '') or ''
                city_name = location.split('،')[-1].strip() if location else (province_name or '')

                contracts = job.get('contract', []) or []
                job_type = ', '.join(contracts) if contracts else ''

                salary = job.get('salary', '') or ''

                benefits_raw = job.get('benefits', []) or []
                benefits = [BENEFIT_LABELS.get(b, b) for b in benefits_raw]

                technologies = job.get('technologies', []) or []

                is_remote = any(
                    kw in job_type for kw in ['دورکاری', 'Remote']
                ) or 'remote_work' in (benefits_raw or [])

                url_path = job.get('url', '')
                url = f"{BASE_URL}{url_path}" if url_path else ''

                is_new = job.get('is_new', False)
                position_levels = job.get('position_levels') or []
                seniority = ', '.join(position_levels) if position_levels else ''

                brand_sector = job.get('brand_sector', '')

                # Client-side category filtering (safety net)
                if not _job_matches_client_filter(job, cfk):
                    continue

                # Level filtering
                if not _job_matches_level(contracts, position_levels, level):
                    continue

                desc_parts = []
                if brand_sector:
                    desc_parts.append(f"حوزه: {brand_sector}")
                if benefits:
                    desc_parts.append(f"مزایا: {', '.join(benefits[:5])}")
                if technologies:
                    desc_parts.append(f"تکنولوژی‌ها: {', '.join(technologies[:5])}")
                description = ' | '.join(desc_parts)

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

            logger.info(f"E-estekhdam page {page}: {len(jobs)} API, {len(results)} total")
            time.sleep(0.3)

        except requests.Timeout:
            logger.error(f"E-estekhdam timeout at page {page}")
            break
        except requests.ConnectionError as e:
            logger.error(f"E-estekhdam connection error: {e}")
            break
        except Exception as e:
            logger.error(f"E-estekhdam error at page {page}: {e}")
            break

    logger.info(f"E-estekhdam total: {len(results)} jobs")
    return results
