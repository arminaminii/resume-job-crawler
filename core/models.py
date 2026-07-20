from django.db import models
import uuid


class Resume(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Extracted data
    full_text = models.TextField(blank=True, default='')
    extracted_skills = models.JSONField(default=list, blank=True)
    extracted_fields = models.JSONField(default=list, blank=True)
    suggested_category = models.CharField(max_length=200, blank=True, default='')
    confidence_score = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'رزومه'
        verbose_name_plural = 'رزومه‌ها'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"رزومه #{self.id}"


class JobSearch(models.Model):
    PLATFORM_CHOICES = [
        ('jobvision', 'جاب‌ویژن'),
        ('e_estekhdam', 'ای‌استخدام'),
        ('irantalent', 'ایران‌تلنت'),
    ]
    LEVEL_CHOICES = [
        ('junior', 'جونیور'),
        ('mid', 'می‌لول'),
        ('senior', 'سنیور'),
        ('manager', 'مدیر'),
        ('all', 'همه سطوح'),
    ]
    TIME_RANGE_CHOICES = [
        ('1', '۱ روز گذشته'),
        ('3', '۳ روز گذشته'),
        ('7', '۷ روز گذشته'),
        ('14', '۱۴ روز گذشته'),
        ('30', '۳۰ روز گذشته'),
        ('all', 'همه'),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='searches')
    created_at = models.DateTimeField(auto_now_add=True)

    platforms = models.JSONField(default=list)
    city = models.CharField(max_length=100, blank=True, default='')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all')
    time_range = models.CharField(max_length=10, choices=TIME_RANGE_CHOICES, default='7')
    custom_keywords = models.CharField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(blank=True, default='')
    total_results = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'جستجو'
        verbose_name_plural = 'جستجوها'
        ordering = ['-created_at']

    def __str__(self):
        return f"جستجو #{self.id} - رزومه #{self.resume_id}"


class JobListing(models.Model):
    search = models.ForeignKey(JobSearch, on_delete=models.CASCADE, related_name='listings')
    platform = models.CharField(max_length=30)

    title = models.CharField(max_length=300, blank=True, default='')
    company = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    province = models.CharField(max_length=100, blank=True, default='')
    salary = models.CharField(max_length=200, blank=True, default='')
    job_type = models.CharField(max_length=100, blank=True, default='')
    seniority_level = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    skills = models.JSONField(default=list, blank=True)
    url = models.URLField(blank=True, default='')
    remote = models.BooleanField(default=False)
    posted_date = models.CharField(max_length=50, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'آگهی استخدام'
        verbose_name_plural = 'آگهی‌های استخدام'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['search', 'platform']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company}"