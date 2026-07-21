import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse

from .models import Resume, JobSearch, JobListing, JobCategory
from .forms import ResumeUploadForm, SearchConfigForm
from .services.ocr_service import extract_resume_text
from .services.bert_classifier import classify_resume, suggest_search_keywords

logger = logging.getLogger(__name__)

# Max seconds each crawler is allowed to run before we kill it
CRAWLER_TIMEOUT_SECONDS = 45


def home(request):
    """Home page - show upload form and resume history."""
    resumes = Resume.objects.all()[:10]
    form = ResumeUploadForm()

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()

            # Extract text using OCR
            try:
                text = extract_resume_text(resume.file.path)
                resume.full_text = text

                logger.info(f"Resume #{resume.id}: OCR extracted {len(text)} chars")

                # Classify with BERT / rule-based
                if text:
                    result = classify_resume(text)
                    resume.extracted_skills = result['skills']
                    resume.extracted_fields = result['fields']
                    resume.suggested_category = result['category']
                    resume.confidence_score = result['confidence']
                    resume.save()

                    logger.info(
                        f"Resume #{resume.id}: category={result['category']}, "
                        f"confidence={result['confidence']}, "
                        f"skills={result['skills']}, "
                        f"fields={result['fields']}"
                    )

                    if result['skills'] or result['fields']:
                        messages.success(request, 'رزومه با موفقیت آپلود و تحلیل شد.')
                    else:
                        messages.warning(
                            request,
                            'رزومه آپلود شد ولی مهارت‌هایی شناسایی نشد. '
                            'لطفاً کلمات کلیدی را دستی وارد کنید.'
                        )
                else:
                    resume.save()
                    messages.warning(
                        request,
                        'متنی از رزومه استخراج نشد. '
                        'اگر فایل PDF تصویری است، مطمئن شوید Poppler نصب شده.'
                    )
            except Exception as e:
                logger.error(f"Resume #{resume.id} processing error: {e}", exc_info=True)
                resume.save()
                messages.error(request, f'خطا در پردازش رزومه: {str(e)[:200]}')

            return redirect('search_config', resume_id=resume.id)

    return render(request, 'core/home.html', {
        'form': form,
        'resumes': resumes,
    })


def upload_resume(request):
    """Handle resume upload via AJAX or form."""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()

            try:
                text = extract_resume_text(resume.file.path)
                resume.full_text = text

                logger.info(f"Resume #{resume.id}: OCR extracted {len(text)} chars")

                if text:
                    result = classify_resume(text)
                    resume.extracted_skills = result['skills']
                    resume.extracted_fields = result['fields']
                    resume.suggested_category = result['category']
                    resume.confidence_score = result['confidence']
                    resume.save()

                    if result['skills'] or result['fields']:
                        messages.success(request, 'رزومه با موفقیت آپلود و تحلیل شد.')
                    else:
                        messages.warning(request, 'مهارت‌هایی شناسایی نشد. کلمات کلیدی را دستی وارد کنید.')
                else:
                    resume.save()
                    messages.warning(request, 'متنی از رزومه استخراج نشد.')
            except Exception as e:
                logger.error(f"Resume #{resume.id} processing error: {e}", exc_info=True)
                resume.save()
                messages.error(request, 'خطا در پردازش رزومه')

            return redirect('search_config', resume_id=resume.id)

    return redirect('home')


def _get_suggested_categories(resume):
    """
    Score all JobCategories against resume skills and text.
    Returns list of (category, score) tuples, sorted by score desc.
    """
    if not resume.extracted_skills and not resume.full_text:
        return []

    categories = JobCategory.objects.filter(is_active=True)
    scored = []

    for cat in categories:
        score = cat.match_score(
            extracted_skills=resume.extracted_skills or [],
            extracted_text=resume.full_text or '',
        )
        if score > 0:
            scored.append((cat, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def search_config(request, resume_id):
    """Configure search parameters for a resume."""
    resume = get_object_or_404(Resume, pk=resume_id)

    # Generate suggested keywords from resume
    suggested_keywords = ''
    if resume.full_text:
        suggested_keywords = suggest_search_keywords(
            resume.full_text,
            resume.extracted_skills or [],
            resume.extracted_fields or [],
        )

    # Smart category suggestions based on OCR/BERT results
    suggested_categories = _get_suggested_categories(resume)
    # Pre-select categories with score > 0.1 (significant match)
    preselected_slugs = [cat.slug for cat, score in suggested_categories if score > 0.1]

    # Get all active categories for the grid
    all_categories = JobCategory.objects.filter(is_active=True).order_by('sort_order', 'name')

    # Determine which platforms/categories are visually checked
    if request.method == 'POST':
        selected_platforms = request.POST.getlist('platforms')
        selected_cats_post = request.POST.getlist('categories')
    else:
        # GET: use defaults + AI suggestions
        selected_platforms = ['jobvision']
        selected_cats_post = preselected_slugs

    if request.method == 'POST':
        form = SearchConfigForm(request.POST)

        # DEBUG: log what we received
        logger.info(f"Search POST: platforms={request.POST.getlist('platforms')}, "
                     f"categories={request.POST.getlist('categories')}, "
                     f"city={request.POST.get('city', '')}, "
                     f"level={request.POST.get('level', '')}")

        # Validate that at least one category is selected
        selected_cats = request.POST.getlist('categories')
        if not selected_cats:
            messages.warning(request, 'لطفاً حداقل یک حوزه شغلی انتخاب کنید.')
            return render(request, 'core/search_config.html', {
                'resume': resume, 'form': form,
                'suggested_keywords': suggested_keywords,
                'suggested_categories': suggested_categories,
                'all_categories': all_categories,
                'preselected_slugs': preselected_slugs,
                'selected_platforms': selected_platforms,
                'selected_cats_post': selected_cats_post,
            })

        if form.is_valid():
            # Build keywords from selected categories + custom input
            cat_keywords = _build_category_keywords(selected_cats)
            custom_kw = form.cleaned_data.get('custom_keywords', '')

            search = JobSearch.objects.create(
                resume=resume,
                platforms=form.cleaned_data['platforms'],
                city=form.cleaned_data['city'],
                level=form.cleaned_data['level'],
                time_range=form.cleaned_data['time_range'],
                custom_keywords=custom_kw,
                selected_categories=selected_cats,
                status='running',
            )

            # Run crawling (with per-crawler timeout protection)
            try:
                crawler_messages = _run_search(search, cat_keywords, suggested_keywords)
                search.status = 'completed'

                for msg in crawler_messages:
                    if 'خطا' in msg or 'not available' in msg.lower() or 'timeout' in msg.lower() or 'زمان' in msg:
                        messages.warning(request, msg)
                    else:
                        messages.success(request, msg)

                if not search.total_results:
                    messages.info(
                        request,
                        'نتیجه‌ای یافت نشد. لطفاً حوزه‌های شغلی بیشتری انتخاب کنید '
                        'یا کلمات کلیدی را تغییر دهید.'
                    )
            except Exception as e:
                search.status = 'failed'
                search.error_message = str(e)
                logger.error(f"Search {search.id} failed: {e}\n{traceback.format_exc()}")
                messages.error(request, f'خطا در جستجو: {str(e)[:200]}')
            finally:
                search.save()

            return redirect('search_results', search_id=search.id)
        else:
            # Form validation failed - show errors to user
            logger.warning(f"Form validation failed: {form.errors}")
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f'{field}: {err}')
    else:
        form = SearchConfigForm()

    return render(request, 'core/search_config.html', {
        'resume': resume,
        'form': form,
        'suggested_keywords': suggested_keywords,
        'suggested_categories': suggested_categories,
        'all_categories': all_categories,
        'preselected_slugs': preselected_slugs,
        'selected_platforms': selected_platforms,
        'selected_cats_post': selected_cats_post,
    })


def _build_category_keywords(selected_slugs: list) -> str:
    """
    Build search keywords from selected category slugs.
    Returns a SHORT, focused keyword string for the API keyword filter.
    Category-based filtering is handled separately via categorySlugs.
    """
    if not selected_slugs:
        return ''

    keywords_parts = set()
    categories = JobCategory.objects.filter(slug__in=selected_slugs, is_active=True)

    for cat in categories:
        # Only add top 3 most specific English skills (avoid generic ones)
        for skill in (cat.skills or [])[:3]:
            keywords_parts.add(skill)
        # Add top 2 positions
        for pos in (cat.positions or [])[:2]:
            # Only add English positions (Persian ones confuse the API)
            if any(c.isascii() for c in pos):
                keywords_parts.add(pos)

    # Limit to max 8 keywords total to keep API query reasonable
    result = list(keywords_parts)[:8]
    return ' '.join(result)


def _run_crawler_safe(crawler_func, crawler_name, **kwargs) -> tuple:
    """
    Run a crawler with a hard timeout so one slow platform can't block others.
    Returns (results_list, status_message_string).
    """
    logger.info(f"[{crawler_name}] Starting crawl (timeout={CRAWLER_TIMEOUT_SECONDS}s)...")
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(crawler_func, **kwargs)
            try:
                results = future.result(timeout=CRAWLER_TIMEOUT_SECONDS)
                msg = f'{crawler_name}: {len(results)} آگهی یافت شد'
                logger.info(f"[{crawler_name}] Done: {len(results)} results")
                return results, msg
            except FuturesTimeoutError:
                logger.warning(f"[{crawler_name}] TIMED OUT after {CRAWLER_TIMEOUT_SECONDS}s")
                return [], f'{crawler_name}: زمان بر ای پلتفرم به پایان رسید. دوباره تلاش کنید یا فقط جاب‌ویژن را انتخاب کنید.'
    except Exception as e:
        logger.error(f"[{crawler_name}] Exception: {e}", exc_info=True)
        return [], f'{crawler_name}: خطا - {str(e)[:80]}'


def _run_search(search: JobSearch, category_keywords: str, auto_keywords: str) -> list:
    """
    Execute the job search across all selected platforms.
    Each crawler runs with a hard timeout so one failure doesn't block others.
    Returns list of status messages to show to user.
    """
    # Build final keywords: category-based + custom + auto from resume
    keywords_parts = []
    if category_keywords:
        keywords_parts.append(category_keywords)
    if search.custom_keywords:
        keywords_parts.append(search.custom_keywords)
    if auto_keywords:
        keywords_parts.append(auto_keywords)
    keywords = ' '.join(keywords_parts)

    logger.info(f"Running search #{search.id}: platforms={search.platforms}, "
                f"keywords='{keywords[:80]}', city={search.city}")

    all_results = []
    status_messages = []

    # Get selected categories for platform-specific slug mapping
    selected_cats = search.selected_categories or []
    jobvision_cats = list(JobCategory.objects.filter(
        slug__in=selected_cats, is_active=True
    ).values_list('jobvision_slug', flat=True).distinct())
    # Filter out empty slugs
    jobvision_cats = [s for s in jobvision_cats if s]

    # --- Jobvision (requests-based, fast REST API) ---
    if 'jobvision' in search.platforms:
        from .crawlers.jobvision_crawler import crawl_jobvision
        results, msg = _run_crawler_safe(
            crawl_jobvision, 'جاب‌ویژن',
            keywords=keywords,
            city=search.city,
            level=search.level,
            time_range=search.time_range,
            max_pages=2,
            category_slugs=jobvision_cats,
        )
        all_results.extend(results)
        status_messages.append(msg)

    # --- E-estekhdam (BS4 + optional Playwright fallback) ---
    if 'e_estekhdam' in search.platforms:
        from .crawlers.estekhdam_crawler import crawl_estekhdam
        results, msg = _run_crawler_safe(
            crawl_estekhdam, 'ای‌استخدام',
            keywords=keywords,
            city=search.city,
            level=search.level,
            time_range=search.time_range,
            max_pages=2,
        )
        all_results.extend(results)
        status_messages.append(msg)

    # --- IranTalent (API + Playwright fallback) ---
    if 'irantalent' in search.platforms:
        from .crawlers.irantalent_crawler import crawl_irantalent
        results, msg = _run_crawler_safe(
            crawl_irantalent, 'ایران‌تلنت',
            keywords=keywords,
            city=search.city,
            level=search.level,
            time_range=search.time_range,
            max_pages=2,
        )
        all_results.extend(results)
        status_messages.append(msg)

    # Save to DB
    search.total_results = len(all_results)
    logger.info(f"Search #{search.id}: total {len(all_results)} results from all platforms")

    for data in all_results:
        JobListing.objects.create(
            search=search,
            platform=data.get('platform', ''),
            title=data.get('title', ''),
            company=data.get('company', ''),
            city=data.get('city', ''),
            province=data.get('province', ''),
            salary=data.get('salary', ''),
            job_type=data.get('job_type', ''),
            seniority_level=data.get('seniority_level', ''),
            description=data.get('description', ''),
            skills=data.get('skills', []),
            url=data.get('url', ''),
            remote=data.get('remote', False),
            posted_date=data.get('posted_date', ''),
        )

    return status_messages


def search_results(request, search_id):
    """Display search results with filtering."""
    search = get_object_or_404(JobSearch, pk=search_id)
    listings = search.listings.all()

    # Apply filters from GET params
    platform_filter = request.GET.get('platform', '')
    city_filter = request.GET.get('city', '')
    level_filter = request.GET.get('level', '')
    keyword_filter = request.GET.get('q', '')

    if platform_filter:
        listings = listings.filter(platform=platform_filter)
    if city_filter:
        listings = listings.filter(city__icontains=city_filter)
    if level_filter:
        listings = listings.filter(seniority_level__icontains=level_filter)
    if keyword_filter:
        from django.db.models import Q
        listings = listings.filter(
            Q(title__icontains=keyword_filter) |
            Q(company__icontains=keyword_filter) |
            Q(description__icontains=keyword_filter) |
            Q(skills__contains=[keyword_filter])
        )

    # Get unique values for filters
    platforms = search.listings.values_list('platform', flat=True).distinct()
    cities = search.listings.values_list('city', flat=True).distinct()
    levels = search.listings.values_list('seniority_level', flat=True).distinct()

    PLATFORM_NAMES = {
        'jobvision': 'جاب‌ویژن',
        'e_estekhdam': 'ای‌استخدام',
        'irantalent': 'ایران‌تلنت',
    }

    # Get selected category names for display
    selected_cat_names = []
    if search.selected_categories:
        cats = JobCategory.objects.filter(slug__in=search.selected_categories)
        selected_cat_names = [c.name for c in cats]

    return render(request, 'core/results.html', {
        'search': search,
        'resume': search.resume,
        'listings': listings,
        'total_count': listings.count(),
        'platform_filter': platform_filter,
        'city_filter': city_filter,
        'level_filter': level_filter,
        'keyword_filter': keyword_filter,
        'platforms': platforms,
        'cities': [c for c in cities if c],
        'levels': [l for l in levels if l],
        'platform_names': PLATFORM_NAMES,
        'selected_cat_names': selected_cat_names,
    })


def delete_resume(request, resume_id):
    """Delete a resume and all related data."""
    resume = get_object_or_404(Resume, pk=resume_id)
    if resume.file:
        resume.file.delete(save=False)
    resume.delete()
    messages.success(request, 'رزومه حذف شد.')
    return redirect('home')


def search_history(request):
    """Show all past searches."""
    searches = JobSearch.objects.select_related('resume').all()[:20]
    return render(request, 'core/history.html', {
        'searches': searches,
    })


def suggest_categories_api(request, resume_id):
    """
    API endpoint: returns category suggestions for a resume.
    Used for dynamic UI updates.
    """
    resume = get_object_or_404(Resume, pk=resume_id)
    suggested = _get_suggested_categories(resume)

    data = []
    for cat, score in suggested:
        data.append({
            'slug': cat.slug,
            'name': cat.name,
            'score': score,
            'color': cat.color,
            'icon_svg': cat.icon_svg,
            'matched_skills': list(set(
                s for s in (resume.extracted_skills or [])
                if s.lower() in set(sk.lower() for sk in (cat.skills or []))
            ))[:5],
        })

    return JsonResponse({'categories': data})