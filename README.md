# سامانه هوشمند تحلیل رزومه و جستجوی استخدام (JobFinder)

یک سامانه وب مبتنی بر Django که با استفاده از هوش مصنوعی، رزومه کاربران را تحلیل کرده و آگهی‌های استخدام مرتبط را از سامانه‌های کاریابی ایرانی جمع‌آوری و نمایش می‌دهد.

## ویژگی‌ها

- **تحلیل رزومه با Tesseract OCR**: استخراج متن از فایل‌های PDF، تصویر، Word و متنی
- **دسته‌بندی با BERT Classification**: تحلیل مهارت‌ها، حوزه کاری و سطح حرفه‌ای با مدل ParsBERT
- **کرال جاب‌ویژن**: استفاده از REST API با فیلتر شهر، سطح و کلمه کلیدی
- **کرال ای‌استخدام**: Web scraping با BeautifulSoup و Playwright (fallback)
- **کرال ایران‌تلنت**: Scraping SPA با Playwright
- **رابط کاربری RTL فارسی**: طراحی تمیز و حرفه‌ای با Bootstrap 5
- **Drag and Drop آپلود**: رابط آپلود فایل با کشیدن و رها کردن
- **فیلتر پیشرفته نتایج**: فیلتر بر اساس سامانه، شهر، سطح و جستجوی متنی

## نصب و راه‌اندازی

```bash
# کلون ریپازیتوری
git clone https://github.com/arminaminii/resume-job-crawler.git
cd resume-job-crawler

# ساخت محیط مجازی
python -m venv venv
source venv/bin/activate

# نصب دیپندنسی‌ها
pip install -r requirements.txt

# نصب Tesseract OCR (Ubuntu/Debian)
sudo apt install tesseract-ocr tesseract-ocr-fa tesseract-ocr-ara
sudo apt install poppler-utils

# نصب Playwright browsers
playwright install chromium

# مایگریشن دیتابیس
python manage.py migrate

# ساخت ادمین
python manage.py createsuperuser

# اجرای سرور
python manage.py runserver
```

## ساختار پروژه

```
├── config/                  # تنظیمات جنگو
├── core/                    # اپ اصلی
│   ├── models.py            # Resume, JobSearch, JobListing
│   ├── views.py             # ویوها
│   ├── forms.py             # فرم‌ها
│   ├── services/
│   │   ├── ocr_service.py   # Tesseract OCR
│   │   └── bert_classifier.py  # BERT Classification
│   ├── crawlers/
│   │   ├── jobvision_crawler.py
│   │   ├── estekhdam_crawler.py
│   │   └── irantalent_crawler.py
│   ├── templates/core/
│   ├── static/
│   └── templatetags/
├── requirements.txt
└── manage.py
```

## تکنولوژی‌ها

Django 5.1 | Tesseract OCR | Transformers (BERT) | Requests | BeautifulSoup | Playwright | Bootstrap 5 RTL | SQLite

## لایسنس

MIT