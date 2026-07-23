"""
E-estekhdam crawler.

API endpoint: POST https://www.e-estekhdam.com/search-api/search?page=N

RESEARCH FINDINGS (tested 2026-07-23):
1. API COMPLETELY IGNORES all search params (q, keyword, search, title, page_size)
2. Pagination WORKS - each page returns 20 DIFFERENT jobs (200 unique across 10 pages)
3. No date fields exist (no created_at, updated_at, etc.)
4. Available fields: id, uuid, title, short_title, brand_name, brand_sector,
   gender, contract, position_levels, provinces, technologies, benefits,
   url, is_new, salary, location
5. 'promoted' field is null (not True/False)
6. No alternative API endpoints (all 404)
7. Website is SPA - no SSR HTML to scrape

STRATEGY:
- Fetch 25 pages (500 jobs) and do HEAVY client-side filtering
- Title match = highest weight, technologies = high, sector = medium
- Province filtering in client-side
- No time filtering possible
- If few/no relevant results found, return top matches anyway (better than nothing)
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

# Province names in E-estekhdam format
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
    """Calculate relevance score based on keyword matches in various fields."""
    if not filter_kws:
        return 0.5

    title = (job_data.get('title', '') or '').lower()
    short_title = (job_data.get('short_title', '') or '').lower()
    sector = (job_data.get('brand_sector', '') or '').lower()
    techs = [t.lower() for t in (job_data.get('technologies', []) or [])]
    levels = [p.lower() for p in (job_data.get('position_levels', []) or [])]
    contracts = [c.lower() for c in (job_data.get('contract', []) or [])]
    benefits = [b.lower() for b in (job_data.get('benefits', []) or [])]

    score = 0.0
    for kw in filter_kws:
        kw_l = kw.lower()
        # Title match (highest weight)
        if kw_l in title:
            score += 5
        if kw_l in short_title:
            score += 4
        # Technologies match (high weight - these are actual skills)
        if any(kw_l in t for t in techs):
            score += 3
        # Sector/industry match
        if kw_l in sector:
            score += 2
        # Level match
        if any(kw_l in l for l in levels):
            score += 2
        # Contract match
        if any(kw_l in c for c in contracts):
            score += 1
        # Benefits match (lowest)
        if any(kw_l in b for b in benefits):
            score += 0.5

    return score


def _job_matches_level(contracts, position_levels, level):
    """Check level match. Pass if no data available."""
    if not level or level == 'all':
        return True
    # E-estekhdam has limited level data - many jobs have null position_levels
    all_text = ' '.join(contracts + position_levels)
    if not all_text.strip():
        return True  # Don't filter out jobs without level data
    lm = {
        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'مقدماتی', 'trainee', 'intern', 'junior'],
        'mid': ['متوسط', 'میان‌رده', 'کارشناس', 'متخصص', 'mid'],
        'senior': ['ارشد', 'سنیور', 'Senior', 'کارشناس ارشد', 'senior'],
        'manager': ['مدیر', 'Manager', 'سرپرست', 'مدیریتی', 'manager'],
    }
    kws = lm.get(level, [])
    if not kws:
        return True
    return any(kw in all_text for kw in kws)


def crawl_estekhdam(keywords='', city='', level='all',
                      time_range='7', max_pages=3,
                      category_slugs=None,
                      client_filter_keywords=None):
    """
    Crawl e-estekhdam.com via its API.
    
    The API ignores search params - returns ALL jobs in pages of 20.
    We fetch many pages and do HEAVY client-side filtering.
    """
    results = []
    seen_ids = set()
    cfk = client_filter_keywords or []
    user_kws = [k.strip().lower() for k in (keywords or '').split() if k.strip()] if keywords else []
    all_kws = list(set(cfk + user_kws))

    # E-estekhdam API ignores body params, but we send anyway for consistency
    body = {}
    if keywords and keywords.strip():
        body['q'] = ' '.join(keywords.strip().split()[:3])

    logger.info(f"E-estekhdam: q='{body.get('q', '')}', city={city}, filter_kws={len(all_kws)}")

    # Fetch 25 pages = 500 jobs (pagination works!)
    fetch_pages = 25

    for page in range(1, fetch_pages + 1):
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

                # Province filtering (client-side since API ignores it)
                provinces = job.get('provinces', []) or []
                if city and city in PROVINCE_MAP:
                    target_province = PROVINCE_MAP[city]
                    if target_province not in provinces and not any(
                        target_province in p for p in provinces
                    ):
                        continue

                # Relevance scoring
                relevance = _calc_relevance(job, all_kws) if all_kws else 0.5

                company = job.get('brand_name', '') or ''
                province_name = ', '.join(provinces) if provinces else ''
                location = job.get('location', '') or ''
                # Extract city from location (last part after comma)
                if location:
                    parts = location.replace('،', ',').split(',')
                    city_name = parts[-1].strip()
                else:
                    city_name = province_name

                contracts = job.get('contract', []) or []
                job_type = ', '.join(contracts) if contracts else ''
                salary = job.get('salary', '') or ''

                benefits_raw = job.get('benefits', []) or []
                benefits = [BENEFIT_LABELS.get(b, b) for b in benefits_raw]
                technologies = job.get('technologies', []) or []

                is_remote = (any(kw in job_type for kw in ['دورکاری', 'Remote']) or
                            'remote_work' in benefits_raw)

                url_path = job.get('url', '')
                url = f"{BASE_URL}{url_path}" if url_path else ''

                position_levels = job.get('position_levels') or []
                seniority = ', '.join(position_levels) if position_levels else ''
                brand_sector = job.get('brand_sector', '')

                # Level filtering (pass if no data)
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

            time.sleep(0.25)
        except requests.Timeout:
            break
        except requests.ConnectionError:
            break
        except Exception as e:
            logger.error(f"E-estekhdam error at page {page}: {e}")
            break

    # Sort by relevance (best matches first)
    results.sort(key=lambda x: x.get('_relevance', 0), reverse=True)
    for r in results:
        r.pop('_relevance', None)

    logger.info(f"E-estekhdam total: {len(results)} jobs")
    return results

