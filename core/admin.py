from django.contrib import admin
from .models import Resume, JobSearch, JobListing


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at', 'suggested_category', 'confidence_score')
    list_filter = ('uploaded_at',)
    search_fields = ('suggested_category',)
    readonly_fields = ('full_text', 'extracted_skills', 'extracted_fields', 'suggested_category', 'confidence_score')


@admin.register(JobSearch)
class JobSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'platforms', 'level', 'time_range')
    readonly_fields = ('total_results', 'error_message')


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'platform', 'city', 'seniority_level')
    list_filter = ('platform', 'city', 'seniority_level')
    search_fields = ('title', 'company', 'skills')