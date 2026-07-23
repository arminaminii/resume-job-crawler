from django.contrib import admin
from .models import Resume, JobSearch, JobListing, JobCategory


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'is_active', 'sort_order', 'parent')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    list_editable = ('is_active', 'sort_order')
    readonly_fields = ('slug',)
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = None  # No date field on this model


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at', 'suggested_category', 'confidence_score')
    list_filter = ('uploaded_at',)
    search_fields = ('suggested_category',)
    readonly_fields = ('full_text', 'extracted_skills', 'extracted_fields',
                       'suggested_category', 'confidence_score')
    date_hierarchy = 'uploaded_at'


@admin.register(JobSearch)
class JobSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'status', 'total_results', 'created_at')
    list_filter = ('status', 'level', 'time_range')
    readonly_fields = ('created_at', 'total_results', 'error_message',
                       'selected_categories', 'platforms', 'city')
    date_hierarchy = 'created_at'


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'platform', 'city', 'seniority_level')
    list_filter = ('platform', 'city')
    search_fields = ('title', 'company')
    readonly_fields = ('created_at', 'search')
    date_hierarchy = 'created_at'
