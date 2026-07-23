from django.db import models
from django.core.validators import RegexValidator
import uuid


hex_color_validator = RegexValidator(
    regex=r'^#[0-9a-fA-F]{6}$',
    message='فقط کد هگز رنگی معتبر (مثل #6366f1) وارد کنید.',
    code='invalid_hex_color',
)


class JobCategory(models.Model):
    """Comprehensive job categories database with skill/position mapping."""
    name = models.CharField(max_length=200, verbose_name='نام حوزه')
    slug = models.CharField(max_length=100, unique=True, verbose_name='اسلاگ')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                               related_name='children', verbose_name='دسته والد')
    icon_svg = models.TextField(blank=True, default='', verbose_name='آیکون SVG')
    color = models.CharField(max_length=7, default='#6366f1', validators=[hex_color_validator],
                               verbose_name='رنگ')

    # Jobvision slug for API filtering
    jobvision_slug = models.CharField(max_length=100, blank=True, default='')
    # E-estekhdam slug
    estekhdam_slug = models.CharField(max_length=100, blank=True, default='')
    # IranTalent slug
    irantalent_slug = models.CharField(max_length=100, blank=True, default='')

    # Skills associated with this category
    skills = models.JSONField(default=list, blank=True, verbose_name='مهارت‌ها')
    # Common job titles/positions in this category
    positions = models.JSONField(default=list, blank=True, verbose_name='موقعیت‌های شغلی')
    # Persian keywords for matching
    keywords_fa = models.JSONField(default=list, blank=True, verbose_name='کلیدواژه‌های فارسی')
    # English keywords for matching
    keywords_en = models.JSONField(default=list, blank=True, verbose_name='کلیدواژه‌های انگلیسی')

    # Education requirements for job tree (min education level)
    # e.g. ['کارشناسی', 'Bachelor', 'لیسانس']
    education = models.JSONField(default=list, blank=True, verbose_name='تحصیلات مورد نیاز')

    # Certifications / licenses required
    certifications = models.JSONField(default=list, blank=True, verbose_name='گواهینامه‌ها')

    # Average salary range description
    salary_range = models.CharField(max_length=200, blank=True, default='', verbose_name='بازه حقوق')

    # Career path / growth potential description
    career_path = models.CharField(max_length=500, blank=True, default='', verbose_name='مسیر پیشرفت')

    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'حوزه شغلی'
        verbose_name_plural = 'حوزه‌های شغلی'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_sub_categories(self):
        """Return active child categories."""
        return self.children.filter(is_active=True)

    def get_full_path(self):
        """Return full path from root to this category."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)

    def get_tree_data(self, _children_cache=None):
        """Return dict for tree JSON serialization.

        Args:
            _children_cache: Optional pre-fetched dict {parent_id: [child]}
                             to avoid N+1 queries. Built by the view layer.
        """
        if _children_cache is not None:
            children = _children_cache.get(self.id, [])
        else:
            children = list(self.children.filter(is_active=True).order_by('sort_order'))
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'color': self.color,
            'icon_svg': self.icon_svg,
            'skills': self.skills or [],
            'positions': self.positions or [],
            'education': self.education or [],
            'certifications': self.certifications or [],
            'salary_range': self.salary_range,
            'career_path': self.career_path,
            'has_children': len(children) > 0,
            'children': [child.get_tree_data(_children_cache) for child in children],
        }
        return data

    def match_score(self, extracted_skills: list, extracted_text: str = '') -> float:
        """
        Calculate how well this category matches extracted resume data.
        Returns a score between 0 and 1.
        """
        if not extracted_skills:
            return 0.0

        skill_set = set(s.lower() for s in extracted_skills)
        cat_skills = set(s.lower() for s in self.skills)
        cat_kw_en = set(k.lower() for k in self.keywords_en)
        cat_kw_fa = set(k.lower() for k in self.keywords_fa)
        cat_positions = set(p.lower() for p in self.positions)

        # Skill overlap (most important)
        skill_overlap = len(skill_set & cat_skills) / max(len(cat_skills), 1)

        # Keyword overlap
        text_lower = extracted_text.lower() if extracted_text else ''
        kw_score = 0
        for kw in cat_kw_en | cat_kw_fa:
            if kw.lower() in text_lower:
                kw_score += 1
        kw_score = min(kw_score / max(len(cat_kw_en | cat_kw_fa), 1), 1.0)

        # Position match in text
        pos_score = 0
        for pos in cat_positions:
            if pos.lower() in text_lower:
                pos_score += 1
        pos_score = min(pos_score / max(len(cat_positions), 1), 1.0)

        # Weighted score
        return round(skill_overlap * 0.5 + kw_score * 0.3 + pos_score * 0.2, 3)


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
    selected_categories = models.JSONField(default=list, blank=True, verbose_name='حوزه‌های انتخابی')
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