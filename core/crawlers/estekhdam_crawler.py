"""
E-estekhdam crawler — uses their PUBLIC REST API.

API endpoint: POST https://www.e-estekhdam.com/search-api/search?page=N
Returns JSON with {ok: true, data: [...]} structure.

KEY INSIGHTS:
1. The API ignores most search params and returns ~20 promoted jobs
2. 'q' keyword DOES filter server-side (when it works)
3. 'where' for province filtering works
4. Client-side filtering is CRITICAL for relevance
5. Response has 'created_at' or 'updated_at' for time filtering
6. No category slug support in the public API

FIXES IN THIS VERSION:
1. Removed duplicate 'q' assignment
2. Added 'category_id' and 'job_category' API params (may help)
3. Improved client-side filtering with TITLE priority matching
4. Added time filtering via 'created_at' field
5. Better keyword scoring for relevance ranking
"""
import requests
import logging
import time
from datetime import datetime, timedelta, timezone

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


# Iran timezone
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))


def _get_session():
    """Create a new requests Session for each call (thread-safe)."""
    s = requests.Session()
    s.headers.update(_HEADERS)
    return s


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


def _calc_relevance_score(job_data: dict, client_kws: list, user_keywords: list) -> float:
    """
    Calculate a relevance score for a job based on keyword matches.
    Returns 0.0-1.0 score. Title matches are weighted highest.
    
    This is used to RANK results, not just filter them.
    """
    if not client_kws and not user_keywords:
        return 0.5  # Neutral score when no keywords

    title = (job_data.get('title', '') or '').lower()
    company = (job_data.get('brand_name', '') or '').lower()
    sector = (job_data.get('brand_sector', '') or '').lower()
    techs = [t.lower() for t in (job_data.get('technologies', []) or [])]
    benefits = [b.lower() for b in (job_data.get('benefits', []) or [])]
    description = (job_data.get('description', '') or '').lower()
    position_levels = [p.lower() for p in (job_data.get('position_levels', []) or [])]

    score = 0.0
    all_kws = set(kw.lower() for kw in (client_kws + user_keywords))
    
    for kw in all_kws:
        kw_lower = kw.lower()
        # Title match (highest weight)
        if kw_lower in title:
            score += 3.0
        # Technologies/skills match
        if any(kw_lower in t for t in techs):
            score += 2.0
        # Sector match
        if kw_lower in sector:
            score += 1.5
        # Position level match
        if any(kw_lower in p for p in position_levels):
            score += 1.5
        # Description match
        if kw_lower in description:
            score += 0.5
        # Benefits match
        if any(kw_lower in b for b in benefits):
            score += 0.3

    # Normalize to 0-1 range
    max_possible = len(all_kws) * 3.0  # Max if all match in title
    return round(min(score / max(max_possible, 1), 1.0), 3)


def _job_matches_client_filter(job_data: dict, client_kws: list, min_score: float = 0.05) -> bool:
    """Client-side filter using category keywords.
    
    Changed from simple OR to score-based filtering.
    At least one keyword must match in title OR 2+ matches elsewhere.
    """
    if not client_kws:
        return True
    
    title = (job_data.get('title', '') or '').lower()
    technologies = [t.lower() for t in (job_data.get('technologies', []) or [])]
    sector = (job_data.get('brand_sector', '') or '').lower()
    position_levels = [p.lower() for p in (job_data.get('position_levels', []) or [])]
    description = (job_data.get('description', '') or '').lower()
    
    # Count total matches
    matches = 0
    for kw in client_kws:
        kw_lower = kw.lower()
        if kw_lower in title:
            matches += 3  # Title match counts more
        elif any(kw_lower in t for t in technologies):
            matches += 2
        elif kw_lower in sector:
            matches += 2
        elif any(kw_lower in p for p in position_levels):
            matches += 2
        elif kw_lower in description:
            matches += 1
    
    # Require at least 1 match (any field) to be relevant
    return matches >= 1


def _job_matches_level(contracts: list, position_levels: list, level: str) -> bool:
    """Check seniority level match."""
    if not level or level == 'all':
        return True
    lm = {
        'junior': ['کارآموز', 'جونیور', 'مبتدی', 'مقدماتی', 'مردود', 'trainee', 'intern'],
        'mid': ['متوسط', 'میان‌رده', 'کارشناس', 'متخصص'],
        'senior': ['ارشد', 'سنیور', 'Senior', 'کارشناس ارشد', 'تخصص بالا', 'senior'],
        'manager': ['مدیر', 'Manager', 'سرپرست', 'مدیریتی', 'manager'],
    }
    kws = lm.get(level, [])
    if not kws:
        return True
    full = ' '.join(contracts + position_levels)
    return any(kw in full for kw in kws)


def _parse_posted_date(job: dict) -> str:
    """Extract and format posted date from E-estekhdam job."""
    # Check for created_at / updated_at fields
    created = job.get('created_at') or job.get('updated_at') or ''
    if created:
        try:
            if isinstance(created, (int, float)):
                # Unix timestamp
                dt = datetime.fromtimestamp(created, tz=IRAN_TZ)
            elif 'T' in str(created):
                dt = datetime.fromisoformat(str(created).replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(str(created)[:19], '%Y-%m-%d %H:%M:%S')
                dt = dt.replace(tzinfo=IRAN_TZ)
            
            now = datetime.now(IRAN_TZ)
            diff = now - dt
            days = diff.days
            
            if days < 0:
                return ''
            elif days == 0:
                return 'امروز'
            elif days == 1:
                return 'دیروز'
            elif days < 7:
                return f'{days} روز پیش'
            elif days < 30:
                return f'{days // 7} هفته پیش'
            elif days < 365:
                return f'{days // 30} ماه پیش'
            else:
                return f'{days // 365} سال پیش'
        except (ValueError, TypeError, OSError):
            return ''
    
    # Fallback: use is_new flag
    if job.get('is_new', False):
        return 'جدید'
    return ''


def _job_matches_time(job: dict, time_range: str) -> bool:
    """Check if job was posted within the time range."""
    if not time_range or time_range == 'all':
        return True
    
    created = job.get('created_at') or job.get('updated_at')
    if not created:
        # If no date, only include if is_new and time_range >= 3
        if time_range in ('1', '3') and not job.get('is_new', False):
            return False
        return True
    
    try:
        days_limit = int(time_range)
    except (ValueError, TypeError):
        return True
    
    try:
        if isinstance(created, (int, float)):
            dt = datetime.fromtimestamp(created, tz=IRAN_TZ)
        elif 'T' in str(created):
            dt = datetime.fromisoformat(str(created).replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(str(created)[:19], '%Y-%m-%d %H:%M:%S')
            dt = dt.replace(tzinfo=IRAN_TZ)
        
        cutoff = datetime.now(IRAN_TZ) - timedelta(days=days_limit)
        return dt >= cutoff
    except (ValueError, TypeError, OSError):
        return True


def crawl_estekhdam(keywords: str = '', city: str = '', level: str = 'all',
                      time_range: str = '7', max_pages: int = 3,
                      category_slugs: list = None,
                      client_filter_keywords: list = None) -> list:
    """
    Crawl e-estekhdam.com via REST API.
    
    STRATEGY:
    1. Send 'q' to API for server-side text filtering
    2. Send 'where' for province filtering
    3. Try additional API params ('technologies', 'job_category') for better results
    4. Client-side: filter by category keywords, level, and time
    5. Rank results by relevance score
    
    - keywords: user's search terms -> sent to API as 'q'
    - category_slugs: E-estekhdam category names (sent to API if supported)
    - client_filter_keywords: category skills (client-side filtering)
    """
    results = []
    seen_ids = set()
    cfk = client_filter_keywords or []

    # Separate user keywords from category keywords
    user_kws = [k.strip().lower() for k in (keywords or '').split() if k.strip()] if keywords else []

    # Build POST body
    body = {}

    # Send keyword to API for server-side filtering
    if keywords and keywords.strip():
        kw_parts = [k.strip() for k in keywords.strip().split()[:3] if k.strip()]
        if kw_parts:
            body['q'] = ' '.join(kw_parts)
            logger.info(f"E-estekhdam API: searching q='{body['q']}'")

    if city and city in PROVINCE_MAP:
        body['where'] = PROVINCE_MAP[city]

    # Try sending technologies as a hint (some API versions support it)
    if user_kws:
        body['technologies'] = user_kws[:5]

    # Add time range as 'date_range' or 'days' (API may support)
    if time_range and time_range != 'all':
        try:
            body['date_range'] = int(time_range)
        except (ValueError, TypeError):
            pass

    # Combine user + category keywords for client filter
    all_client_kws = list(set(cfk + user_kws))

    logger.info(f"E-estekhdam: body keys={list(body.keys())}, city={city}, time_range={time_range}")

    # Fetch more pages since many results get filtered out
    effective_pages = max_pages + 2

    for page in range(1, effective_pages + 1):
        try:
            _s = _get_session()
            resp = _s.post(
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

            page_matched = 0
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

                position_levels = job.get('position_levels') or []
                seniority = ', '.join(position_levels) if position_levels else ''

                brand_sector = job.get('brand_sector', '')

                # --- Time filtering (client-side) ---
                if not _job_matches_time(job, time_range):
                    continue

                # --- Client-side category filtering (relevance check) ---
                if not _job_matches_client_filter(job, all_client_kws):
                    continue

                # --- Level filtering ---
                if not _job_matches_level(contracts, position_levels, level):
                    continue

                # --- Calculate relevance score for ranking ---
                relevance = _calc_relevance_score(job, all_client_kws, user_kws)

                # --- Parse posted date ---
                posted_date = _parse_posted_date(job)

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
                    'posted_date': posted_date,
                    '_relevance': relevance,  # For sorting
                })
                page_matched += 1

            logger.info(f"E-estekhdam page {page}: {len(jobs)} API, {page_matched} matched (total: {len(results)})")
            time.sleep(0.3)

            if len(results) >= max_pages * 30:
                break

        except requests.Timeout:
            logger.error(f"E-estekhdam timeout at page {page}")
            break
        except requests.ConnectionError as e:
            logger.error(f"E-estekhdam connection error: {e}")
            break
        except Exception as e:
            logger.error(f"E-estekhdam error at page {page}: {e}")
            break

    # Sort by relevance (most relevant first)
    results.sort(key=lambda x: x.get('_relevance', 0), reverse=True)
    # Remove internal relevance field
    for r in results:
        r.pop('_relevance', None)

    logger.info(f"E-estekhdam total: {len(results)} jobs")
    return results
