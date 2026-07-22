"""
E-estekhdam crawler — handles BROKEN API gracefully.

API endpoint: POST https://www.e-estekhdam.com/search-api/search?page=N

CRITICAL RESEARCH FINDINGS (tested 2026-07-22):
1. The API COMPLETELY IGNORES the 'q' parameter — always returns same 20 promoted jobs
2. NO 'created_at' or 'updated_at' field exists in the response
3. No alternative API endpoints exist (all 404)
4. The only available data: id, title, brand_name, brand_sector, contract,
   position_levels, provinces, technologies, benefits, promoted flag

STRATEGY:
- Accept that this API only returns promoted jobs
- Use HEAVY client-side filtering for relevance
- Score results by how many category keywords match in title/sector/technologies
- Sort by relevance (most relevant promoted jobs first)
- If no jobs pass the relevance filter, return empty list
- Fetch many pages to get more promoted jobs to filter from
"""
import requests
import logging
import time

logger = logging.getLogger(__name__)

BASE_URL = "https://www.e-estekhdam.com"
SEARCH_API = f"{BASE_URL}/search-api/search"

_HEADERS = {
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


def _get_session():
    s = requests.Session()
    s.headers.update(_HEADERS)
    return s


def _calc_relevance(job_data: dict, filter_kws: list) -> float:
    """
    Calculate relevance score. Title match = 5, sector = 3, technologies = 2, etc.
    Returns 0.0 if no keywords match at all.
    """
    if not filter_kws:
        return 0.5

    title = (job_data.get('title', '') or '').lower()
    short_title = (job_data.get('short_title', '') or '').lower()
    company = (job_data.get('brand_name', '') or '').lower()
    sector = (job_data.get('brand_sector', '') or '').lower()
    techs = [t.lower() for t in (job_data.get('technologies', []) or [])]
    levels = [p.lower() for p in (job_data.get('position_levels', []) or [])]
    contracts = [c.lower() for c in (job_data.get('contract', []) or [])]
    benefits = [b.lower() for b in (job_data.get('benefits', []) or [])]

    score = 0.0
    for kw in filter_kws:
        kw_l = kw.lower()
        if kw_l in title:
            score += 5
        if kw_l in short_title:
            score += 5
        if kw_l in sector:
            score += 3
        if any(kw_l in t for t in techs):
            score += 2
        if any(kw_l in l for l in levels):
            score += 2
        if any(kw_l in c for c in contracts):
            score += 1
        if any(kw_l in b for b in benefits):
            score += 0.5

    return score


def _job_matches_level(contracts, position_levels, level):
    if not level or level == 'all':
        return True
    lm = {
        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'مقدماتی', 'trainee', 'intern'],
        'mid': ['متوسط', 'میان‌رده', 'کارشناس', 'متخصص'],
        'senior': ['ارشد', 'سنیور', 'Senior', 'کارشناس ارشد', 'senior'],
        'manager': ['مدیر', 'Manager', 'سرپرست', 'مدیریتی', 'manager'],
    }
    kws = lm.get(level, [])
    if not kws:
        return True
    full = ' '.join(contracts + position_levels)
    return any(kw in full for kw in kws)


def crawl_estekhdam(keywords='', city='', level='all',
                      time_range='7', max_pages=3,
                      category_slugs=None,
                      client_filter_keywords=None):
    """
    Crawl e-estekhdam.com via its BROKEN API.
    
    The API ignores all search params and returns promoted jobs only.
    We filter heavily client-side and sort by relevance.
    No time filtering is possible (no date field in response).
    """
    results = []
    seen_ids = set()
    cfk = client_filter_keywords or []
    user_kws = [k.strip().lower() for k in (keywords or '').split() if k.strip()] if keywords else []
    all_kws = list(set(cfk + user_kws))

    body = {}
    if keywords and keywords.strip():
        body['q'] = ' '.join(keywords.strip().split()[:3])
    if city and city in PROVINCE_MAP:
        body['where'] = PROVINCE_MAP[city]

    logger.info(f"E-estekhdam: q='{body.get('q','')}', city={city}, filter_kws={len(all_kws)}")
    logger.warning("E-estekhdam API is BROKEN - only returns promoted jobs. Using client-side filtering.")

    # Fetch many pages to get more promoted jobs to filter
    effective_pages = max(max_pages * 3, 10)

    for page in range(1, effective_pages + 1):
        try:
            _s = _get_session()
            resp = _s.post(f"{SEARCH_API}?page={page}", json=body, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if not data.get('ok'):
                break

            jobs = data.get('data', [])
            if not jobs:
                break

            for job in jobs:
                jid = job.get('id')
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)

                title = job.get('title', '') or job.get('short_title', '')
                if not title:
                    continue

                # Skip if NO keywords match at all
                if all_kws:
                    relevance = _calc_relevance(job, all_kws)
                    if relevance < 1.0:  # At least one meaningful match required
                        continue
                else:
                    relevance = 0.5

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

                is_remote = any(kw in job_type for kw in ['دورکاری', 'Remote']) or 'remote_work' in benefits_raw

                url_path = job.get('url', '')
                url = f"{BASE_URL}{url_path}" if url_path else ''

                position_levels = job.get('position_levels') or []
                seniority = ', '.join(position_levels) if position_levels else ''
                brand_sector = job.get('brand_sector', '')

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
                    'posted_date': '',
                    '_relevance': relevance,
                })

            time.sleep(0.3)
            if len(results) >= max_pages * 30:
                break
        except requests.Timeout:
            break
        except requests.ConnectionError:
            break
        except Exception as e:
            logger.error(f"E-estekhdam error at page {page}: {e}")
            break

    # Sort by relevance
    results.sort(key=lambda x: x.get('_relevance', 0), reverse=True)
    for r in results:
        r.pop('_relevance', None)

    logger.info(f"E-estekhdam total: {len(results)} jobs (from promoted only)")
    return results
