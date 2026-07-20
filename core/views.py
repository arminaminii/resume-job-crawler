import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .models import Resume, JobSearch, JobListing
from .forms import ResumeUploadForm, SearchConfigForm
from .services.ocr_service import extract_resume_text
from .services.bert_classifier import classify_resume, suggest_search_keywords

logger = logging.getLogger(__name__)


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

                # Classify with BERT
                if text:
                    result = classify_resume(text)
                    resume.extracted_skills = result['skills']
                    resume.extracted_fields = result['fields']
                    resume.suggested_category = result['category']
                    resume.confidence_score = result['confidence']
                    resume.save()
                    messages.success(request, 'رزومه با موفقیت آپلود و تحلیل شد.')
                else:
                    resume.save()
                    messages.warning(request, 'رزومه آپلود شد ولی متنی استخراج نشد.')
            except Exception as e:
                logger.error(f"Resume processing error: {e}")
                resume.save()
                messages.error(request, f'خطا در پردازش رزومه: {str(e)}')

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

                if text:
                    result = classify_resume(text)
                    resume.extracted_skills = result['skills']
                    resume.extracted_fields = result['fields']
                    resume.suggested_category = result['category']
                    resume.confidence_score = result['confidence']
                    resume.save()
                    messages.success(request, 'رزومه با موفقیت آپلود و تحلیل شد.')
                else:
                    resume.save()
                    messages.warning(request, 'متنی از رزومه استخراج نشد. لطفاً فایل متنی آپلود کنید.')
            except Exception as e:
                logger.error(f"Resume processing error: {e}")
                resume.save()
                messages.error(request, f'خطا در پردازش رزومه')

            return redirect('search_config', resume_id=resume.id)

    return redirect('home')


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

    if request.method == 'POST':
        form = SearchConfigForm(request.POST)
        if form.is_valid():
            search = JobSearch.objects.create(
                resume=resume,
                platforms=form.cleaned_data['platforms'],
                city=form.cleaned_data['city'],
                level=form.cleaned_data['level'],
                time_range=form.cleaned_data['time_range'],
                custom_keywords=form.cleaned_data['custom_keywords'],
                status='running',
            )

            # Run crawling (could be async with Celery in production)
            try:
                _run_search(search, suggested_keywords)
                search.status = 'completed'
            except Exception as e:
                search.status = 'failed'
                search.error_message = str(e)
                logger.error(f"Search {search.id} failed: {e}")
            finally:
                search.save()

            return redirect('search_results', search_id=search.id)
    else:
        form = SearchConfigForm(initial={
            'custom_keywords': suggested_keywords,
        })

    return render(request, 'core/search_config.html', {
        'resume': resume,
        'form': form,
        'suggested_keywords': suggested_keywords,
    })


def _run_search(search: JobSearch, auto_keywords: str):
    """Execute the job search across all selected platforms."""
    # Build final keywords: custom + auto from resume
    keywords_parts = []
    if search.custom_keywords:
        keywords_parts.append(search.custom_keywords)
    if auto_keywords:
        keywords_parts.append(auto_keywords)
    keywords = ' '.join(keywords_parts)

    all_results = []

    if 'jobvision' in search.platforms:
        from .crawlers.jobvision_crawler import crawl_jobvision
        results = crawl_jobvision(
            keywords=keywords,
            city=search.city,
            level=search.level,
            time_range=search.time_range,
            max_pages=3,
        )
        all_results.extend(results)
        logger.info(f"Jobvision: {len(results)} results")

    if 'e_estekhdam' in search.platforms:
        from .crawlers.estekhdam_crawler import crawl_estekhdam
        results = crawl_estekhdam(
            keywords=keywords,
            city=search.city,
            level=search.level,
            time_range=search.time_range,
            max_pages=3,
        )
        all_results.extend(results)
        logger.info(f"E-estekhdam: {len(results)} results")

    if 'irantalent' in search.platforms:
        from .crawlers.irantalent_crawler import crawl_irantalent
        results = crawl_irantalent(
            keywords=keywords,
            city=search.city,
            level=search.level,
            time_range=search.time_range,
            max_pages=3,
        )
        all_results.extend(results)
        logger.info(f"IranTalent: {len(results)} results")

    # Save to DB
    search.total_results = len(all_results)
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