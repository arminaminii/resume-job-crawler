"""
Comprehensive job categories seed data with THREE PARALLEL TREES:
  1. Education-based (تحصیلی): University majors → Specializations → Job titles → Skills
  2. Skills-based (مهارتی): Tech areas → Specializations → Titles → Skills
  3. Work-history (سوابق شغلی): Industry sectors → Departments → Roles → Skills

Each leaf node has platform slugs (jobvision, irantalent, estekhdam),
skills, positions, keywords, education requirements, and career paths.

Run: python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from core.models import JobCategory


ICONS = {
    "developer": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
    "frontend": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><line x1=\"3\" y1=\"9\" x2=\"21\" y2=\"9\"/><line x1=\"9\" y1=\"21\" x2=\"9\" y2=\"9\"/></svg>",
    "mobile": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"5\" y=\"2\" width=\"14\" height=\"20\" rx=\"2\"/><line x1=\"12\" y1=\"18\" x2=\"12.01\" y2=\"18\"/></svg>",
    "data": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\"/><path d=\"M21 12c0 1.66-4 3-9 3s-9-1.34-9-3\"/><path d=\"M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5\"/></svg>",
    "ai": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7l10 5 10-5-10-5z\"/><path d=\"M2 17l10 5 10-5\"/><path d=\"M2 12l10 5 10-5\"/></svg>",
    "devops": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
    "design": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 19l7-7 3 3-7 7-3-3z\"/><path d=\"M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z\"/><path d=\"M2 2l7.586 7.586\"/><circle cx=\"11\" cy=\"11\" r=\"2\"/></svg>",
    "marketing": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M18 3a3 3 0 00-3 3v12a3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3H6a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3V6a3 3 0 00-3-3 3 3 0 00-3 3 3 3 0 003 3h12a3 3 0 003-3 3 3 0 00-3-3z\"/></svg>",
    "finance": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"/><path d=\"M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6\"/></svg>",
    "hr": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2\"/><circle cx=\"9\" cy=\"7\" r=\"4\"/><path d=\"M23 21v-2a4 4 0 00-3-3.87\"/><path d=\"M16 3.13a4 4 0 010 7.75\"/></svg>",
    "management": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "network": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"2\" y=\"2\" width=\"20\" height=\"8\" rx=\"2\"/><rect x=\"2\" y=\"14\" width=\"20\" height=\"8\" rx=\"2\"/><line x1=\"6\" y1=\"6\" x2=\"6.01\" y2=\"6\"/><line x1=\"6\" y1=\"18\" x2=\"6.01\" y2=\"18\"/></svg>",
    "security": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z\"/></svg>",
    "content": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z\"/><polyline points=\"14 2 14 8 20 8\"/><line x1=\"16\" y1=\"13\" x2=\"8\" y2=\"13\"/><line x1=\"16\" y1=\"17\" x2=\"8\" y2=\"17\"/></svg>",
    "sales": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"23 6 13.5 15.5 8.5 10.5 1 18\"/><polyline points=\"17 6 23 6 23 12\"/></svg>",
    "medical": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 12h-4l-3 9L9 3l-3 9H2\"/></svg>",
    "engineering": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
    "qa": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M9 11l3 3L22 4\"/><path d=\"M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11\"/></svg>",
    "game": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"6\" y1=\"11\" x2=\"10\" y2=\"11\"/><line x1=\"8\" y1=\"9\" x2=\"8\" y2=\"13\"/><line x1=\"15\" y1=\"12\" x2=\"15.01\" y2=\"12\"/><line x1=\"18\" y1=\"10\" x2=\"18.01\" y2=\"10\"/></svg>",
    "legal": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7v10l10 5 10-5V7L12 2z\"/><path d=\"M12 22V12\"/><path d=\"M22 7L12 12 2 7\"/></svg>",
    "education": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z\"/><path d=\"M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z\"/></svg>",
    "transport": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"1\" y=\"3\" width=\"15\" height=\"13\"/><polygon points=\"16 8 20 8 23 11 23 16 16 16 16 8\"/><circle cx=\"5.5\" cy=\"18.5\" r=\"2.5\"/><circle cx=\"18.5\" cy=\"18.5\" r=\"2.5\"/></svg>",
    "factory": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M2 20a2 2 0 002 2h16a2 2 0 002-2V8l-7 5V8l-7 5V4a2 2 0 00-2-2H4a2 2 0 00-2 2z\"/><line x1=\"17\" y1=\"17\" x2=\"17\" y2=\"17.01\"/></svg>",
    "building": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
    "phone": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z\"/></svg>"
}


ALL_CATEGORIES = [
    {
        "slug": "edu-eng",
        "name": "مهندسی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#3b82f6",
        "sort_order": 10,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "مهندسی",
            "مهندس"
        ],
        "keywords_en": [
            "engineering",
            "engineer"
        ],
        "education": [
            "کارشناسی مهندسی",
            "کارشناسی ارشد",
            "دکتری"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "مهندس جونیور ← مهندس متخصص ← مهندس ارشد ← مدیر فنی ← مدیر ارشد مهندسی",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-eng-cs",
        "name": "مهندسی کامپیوتر",
        "parent_slug": "edu-eng",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#6366f1",
        "sort_order": 1,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "مهندسی کامپیوتر",
            "مهندسی نرم‌افزار",
            "مهندسی سخت‌افزار",
            "علوم کامپیوتر"
        ],
        "keywords_en": [
            "computer engineering",
            "software engineering",
            "computer science",
            "CS"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی ارشد نرم‌افزار"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "برنامه‌نویس جونیور ← برنامه‌نویس ارشد ← معماری نرم‌افزار ← CTO",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-sw",
        "name": "مهندسی نرم‌افزار",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#8b5cf6",
        "sort_order": 1,
        "skills": [
            "Python",
            "Java",
            "C#",
            "JavaScript",
            "TypeScript",
            "Go",
            "Rust",
            "SQL",
            "Git",
            "Linux",
            "Docker",
            "REST API",
            "Microservices",
            "Object-Oriented",
            "Design Patterns",
            "Unit Testing",
            "CI/CD",
            "Agile",
            "Scrum"
        ],
        "positions": [
            "برنامه‌نویس بک‌اند",
            "توسعه‌دهنده نرم‌افزار",
            "مهندس نرم‌افزار",
            "Backend Developer",
            "Software Engineer",
            "Full Stack Developer"
        ],
        "keywords_fa": [
            "نرم‌افزار",
            "برنامه‌نویسی",
            "توسعه",
            "بک‌اند",
            "backend",
            "فول‌استک"
        ],
        "keywords_en": [
            "software",
            "programming",
            "backend",
            "development",
            "coder",
            "full stack"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی ارشد نرم‌افزار",
            "دکتری مهندسی نرم‌افزار"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان (جونیور تا سنیور)",
        "career_path": "Junior Dev ← Mid Dev ← Senior Dev ← Tech Lead ← Software Architect ← CTO",
        "jobvision_slug": "software",
        "estekhdam_slug": "software",
        "irantalent_slug": "software-engineering"
    },
    {
        "slug": "edu-sw-py",
        "name": "توسعه‌دهنده پایتون",
        "parent_slug": "edu-sw",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 3,
        "skills": [
            "Python",
            "Django",
            "Flask",
            "FastAPI",
            "Celery",
            "PostgreSQL",
            "Redis",
            "Docker",
            "REST API",
            "SQLAlchemy",
            "Pytest",
            "Pandas",
            "Scrapy",
            "gRPC"
        ],
        "positions": [
            "برنامه‌نویس پایتون",
            "توسعه‌دهنده بک‌اند پایتون",
            "Python Developer",
            "Django Developer",
            "Backend Engineer"
        ],
        "keywords_fa": [
            "پایتون",
            "جنگو",
            "فلسک",
            "دجانجو",
            "فست‌آپی"
        ],
        "keywords_en": [
            "python",
            "django",
            "flask",
            "fastapi"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۲۰ - ۶۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "python",
        "estekhdam_slug": "",
        "irantalent_slug": "python"
    },
    {
        "slug": "edu-sw-java",
        "name": "توسعه‌دهنده جاوا",
        "parent_slug": "edu-sw",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 4,
        "skills": [
            "Java",
            "Spring Boot",
            "Spring Cloud",
            "Maven",
            "Gradle",
            "Hibernate",
            "PostgreSQL",
            "Microservices",
            "Kafka",
            "Redis",
            "Docker",
            "Kubernetes",
            "Jenkins"
        ],
        "positions": [
            "برنامه‌نویس جاوا",
            "توسعه‌دهنده Spring",
            "Java Developer",
            "Backend Engineer Java"
        ],
        "keywords_fa": [
            "جاوا",
            "اسپرینگ",
            "جاوا اسپرینگ",
            "جاوا اسپرینگ بوت"
        ],
        "keywords_en": [
            "java",
            "spring",
            "spring boot"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۲۰ - ۷۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "java",
        "estekhdam_slug": "",
        "irantalent_slug": "java"
    },
    {
        "slug": "edu-sw-csharp",
        "name": "توسعه‌دهنده دات‌نت",
        "parent_slug": "edu-sw",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 5,
        "skills": [
            "C#",
            ".NET Core",
            "ASP.NET",
            "Entity Framework",
            "SQL Server",
            "Azure",
            "Blazor",
            "WPF",
            "LINQ",
            "Docker"
        ],
        "positions": [
            "برنامه‌نویس سی‌شارپ",
            "توسعه‌دهنده دات‌نت",
            ".NET Developer"
        ],
        "keywords_fa": [
            "سی شارپ",
            "دات نت",
            "سی‌شارپ"
        ],
        "keywords_en": [
            "c#",
            ".net",
            "dotnet"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۱۸ - ۵۵ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "csharp",
        "estekhdam_slug": "",
        "irantalent_slug": "csharp"
    },
    {
        "slug": "edu-sw-nodejs",
        "name": "توسعه‌دهنده نود جی‌اس",
        "parent_slug": "edu-sw",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 6,
        "skills": [
            "Node.js",
            "Express",
            "NestJS",
            "TypeScript",
            "MongoDB",
            "PostgreSQL",
            "Redis",
            "Socket.IO",
            "Docker",
            "GraphQL"
        ],
        "positions": [
            "برنامه‌نویس نود",
            "Node Developer",
            "Full Stack Developer"
        ],
        "keywords_fa": [
            "نود جی‌اس",
            "نود",
            "Node.js",
            "نست جی‌اس"
        ],
        "keywords_en": [
            "nodejs",
            "node.js",
            "express",
            "nestjs"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۱۸ - ۵۵ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-sw-php",
        "name": "توسعه‌دهنده پی‌اچ‌پی",
        "parent_slug": "edu-sw",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 7,
        "skills": [
            "PHP",
            "Laravel",
            "WordPress",
            "MySQL",
            "Redis",
            "Docker",
            "Composer",
            "PHPUnit",
            "REST API",
            "Vue.js"
        ],
        "positions": [
            "برنامه‌نویس پی‌اچ‌پی",
            "Laravel Developer"
        ],
        "keywords_fa": [
            "پی‌اچ‌پی",
            "لاراول",
            "وردپرس"
        ],
        "keywords_en": [
            "php",
            "laravel",
            "wordpress"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۴۵ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-sw-go",
        "name": "توسعه‌دهنده گو",
        "parent_slug": "edu-sw",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 8,
        "skills": [
            "Go",
            "Gin",
            "gRPC",
            "Docker",
            "Kubernetes",
            "PostgreSQL",
            "Redis",
            "Microservices",
            "Prometheus"
        ],
        "positions": [
            "Go Developer",
            "Backend Engineer Go"
        ],
        "keywords_fa": [
            "زبان گو",
            "گولنگ"
        ],
        "keywords_en": [
            "go",
            "golang"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۲۵ - ۷۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-sw-rust",
        "name": "توسعه‌دهنده رست",
        "parent_slug": "edu-sw",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 9,
        "skills": [
            "Rust",
            "Actix",
            "Tokio",
            "WebAssembly",
            "Docker",
            "Systems Programming"
        ],
        "positions": [
            "Rust Developer",
            "Systems Engineer"
        ],
        "keywords_fa": [
            "رست",
            "راست"
        ],
        "keywords_en": [
            "rust"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۳۰ - ۸۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-fe",
        "name": "توسعه‌دهنده فرانت‌اند",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><line x1=\"3\" y1=\"9\" x2=\"21\" y2=\"9\"/><line x1=\"9\" y1=\"21\" x2=\"9\" y2=\"9\"/></svg>",
        "color": "#f59e0b",
        "sort_order": 2,
        "skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "TypeScript",
            "React",
            "Vue.js",
            "Angular",
            "Next.js",
            "Nuxt.js",
            "Tailwind CSS",
            "SASS",
            "Webpack",
            "Vite",
            "Responsive Design",
            "PWA",
            "Redux",
            "Jest",
            "Cypress",
            "Storybook",
            "Figma"
        ],
        "positions": [
            "طراح و توسعه‌دهنده وب",
            "فرانت‌اند دولوپر",
            "Frontend Developer",
            "React Developer",
            "UI Developer",
            "Web Developer"
        ],
        "keywords_fa": [
            "فرانت‌اند",
            "وب",
            "رابط کاربری",
            "React",
            "ویو",
            "وب‌دولوپر"
        ],
        "keywords_en": [
            "frontend",
            "web",
            "react",
            "vue",
            "angular",
            "ui",
            "web developer"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT",
            "مدرک معادل"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان",
        "career_path": "Junior Frontend ← Frontend Dev ← Senior Frontend ← Frontend Architect ← UI/UX Tech Lead",
        "jobvision_slug": "frontend",
        "estekhdam_slug": "",
        "irantalent_slug": "frontend"
    },
    {
        "slug": "edu-fe-react",
        "name": "توسعه‌دهنده ریکت",
        "parent_slug": "edu-fe",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><line x1=\"3\" y1=\"9\" x2=\"21\" y2=\"9\"/><line x1=\"9\" y1=\"21\" x2=\"9\" y2=\"9\"/></svg>",
        "color": "#06b6d4",
        "sort_order": 11,
        "skills": [
            "React",
            "Next.js",
            "TypeScript",
            "Redux",
            "React Query",
            "Tailwind CSS",
            "Jest",
            "Cypress",
            "Storybook",
            "React Native",
            "Remix"
        ],
        "positions": [
            "React Developer",
            "Next.js Developer",
            "Frontend Engineer",
            "React Native Developer"
        ],
        "keywords_fa": [],
        "keywords_en": [
            "react",
            "next.js",
            "redux",
            "react native"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۲۰ - ۶۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-fe-vue",
        "name": "توسعه‌دهنده ویو",
        "parent_slug": "edu-fe",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><line x1=\"3\" y1=\"9\" x2=\"21\" y2=\"9\"/><line x1=\"9\" y1=\"21\" x2=\"9\" y2=\"9\"/></svg>",
        "color": "#06b6d4",
        "sort_order": 12,
        "skills": [
            "Vue.js",
            "Nuxt.js",
            "Vuex",
            "Pinia",
            "Vuetify",
            "TypeScript",
            "Vite"
        ],
        "positions": [
            "Vue Developer",
            "Nuxt Developer"
        ],
        "keywords_fa": [],
        "keywords_en": [
            "vue",
            "nuxt"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۱۵ - ۴۵ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-fe-angular",
        "name": "توسعه‌دهنده انگولار",
        "parent_slug": "edu-fe",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><line x1=\"3\" y1=\"9\" x2=\"21\" y2=\"9\"/><line x1=\"9\" y1=\"21\" x2=\"9\" y2=\"9\"/></svg>",
        "color": "#06b6d4",
        "sort_order": 13,
        "skills": [
            "Angular",
            "TypeScript",
            "RxJS",
            "NgRx",
            "Material UI",
            "Jasmine",
            "Karma"
        ],
        "positions": [
            "Angular Developer",
            "Frontend Engineer"
        ],
        "keywords_fa": [],
        "keywords_en": [
            "angular",
            "typescript"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mobile",
        "name": "توسعه‌دهنده موبایل",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"5\" y=\"2\" width=\"14\" height=\"20\" rx=\"2\"/><line x1=\"12\" y1=\"18\" x2=\"12.01\" y2=\"18\"/></svg>",
        "color": "#ec4899",
        "sort_order": 3,
        "skills": [
            "Flutter",
            "React Native",
            "Swift",
            "Kotlin",
            "Dart",
            "iOS",
            "Android",
            "Firebase",
            "REST API",
            "SQLite",
            "Xcode",
            "Android Studio",
            "App Store",
            "Google Play"
        ],
        "positions": [
            "توسعه‌دهنده موبایل",
            "Mobile Developer",
            "iOS Developer",
            "Android Developer",
            "Flutter Developer"
        ],
        "keywords_fa": [
            "موبایل",
            "اندروید",
            "آی‌او‌اس",
            "فلاتر",
            "سوئیفت",
            "کاتلین"
        ],
        "keywords_en": [
            "mobile",
            "android",
            "ios",
            "flutter",
            "react native",
            "swift",
            "kotlin"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "کارشناسی IT"
        ],
        "certifications": [],
        "salary_range": "۲۰ - ۶۰ میلیون تومان",
        "career_path": "Junior Mobile ← Mobile Dev ← Senior Mobile ← Mobile Tech Lead",
        "jobvision_slug": "mobile",
        "estekhdam_slug": "",
        "irantalent_slug": "mobile"
    },
    {
        "slug": "edu-mob-flutter",
        "name": "توسعه‌دهنده فلاتر",
        "parent_slug": "edu-mobile",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"5\" y=\"2\" width=\"14\" height=\"20\" rx=\"2\"/><line x1=\"12\" y1=\"18\" x2=\"12.01\" y2=\"18\"/></svg>",
        "color": "#ec4899",
        "sort_order": 15,
        "skills": [
            "Flutter",
            "Dart",
            "Firebase",
            "BLoC",
            "GetX",
            "iOS",
            "Android"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "flutter",
            "dart"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mob-native-ios",
        "name": "توسعه‌دهنده آی‌او‌اس",
        "parent_slug": "edu-mobile",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"5\" y=\"2\" width=\"14\" height=\"20\" rx=\"2\"/><line x1=\"12\" y1=\"18\" x2=\"12.01\" y2=\"18\"/></svg>",
        "color": "#ec4899",
        "sort_order": 16,
        "skills": [
            "Swift",
            "SwiftUI",
            "UIKit",
            "Xcode",
            "Core Data",
            "Combine",
            "ARKit"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "ios",
            "swift",
            "swiftui"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mob-native-android",
        "name": "توسعه‌دهنده اندروید",
        "parent_slug": "edu-mobile",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"5\" y=\"2\" width=\"14\" height=\"20\" rx=\"2\"/><line x1=\"12\" y1=\"18\" x2=\"12.01\" y2=\"18\"/></svg>",
        "color": "#ec4899",
        "sort_order": 17,
        "skills": [
            "Kotlin",
            "Jetpack Compose",
            "Android SDK",
            "Coroutines",
            "Room",
            "Retrofit"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "android",
            "kotlin",
            "jetpack compose"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mob-rn",
        "name": "توسعه‌دهنده ریککت‌نتیو",
        "parent_slug": "edu-mobile",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"5\" y=\"2\" width=\"14\" height=\"20\" rx=\"2\"/><line x1=\"12\" y1=\"18\" x2=\"12.01\" y2=\"18\"/></svg>",
        "color": "#ec4899",
        "sort_order": 18,
        "skills": [
            "React Native",
            "TypeScript",
            "Expo",
            "Redux",
            "React Navigation",
            "Native Modules"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "react native",
            "expo"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-devops",
        "name": "داوآپس و زیرساخت ابری",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#f97316",
        "sort_order": 4,
        "skills": [
            "Docker",
            "Kubernetes",
            "AWS",
            "Azure",
            "GCP",
            "Linux",
            "CI/CD",
            "Jenkins",
            "GitHub Actions",
            "Terraform",
            "Ansible",
            "Prometheus",
            "Grafana",
            "Nginx",
            "Helm",
            "ArgoCD",
            "Vault"
        ],
        "positions": [
            "مهندس داوآپس",
            "DevOps Engineer",
            "Cloud Engineer",
            "Site Reliability Engineer",
            "SRE",
            "Platform Engineer",
            "Infrastructure Engineer"
        ],
        "keywords_fa": [
            "داوآپس",
            "زیرساخت",
            "اکس",
            "دکر",
            "کوبرنیتیس",
            "سیستم",
            "سایت ریلیابیلیتی"
        ],
        "keywords_en": [
            "devops",
            "cloud",
            "aws",
            "docker",
            "kubernetes",
            "sre",
            "infrastructure"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "شبکه",
            "مجوز AWS/Azure"
        ],
        "certifications": [],
        "salary_range": "۲۵ - ۸۰ میلیون تومان",
        "career_path": "Sysadmin ← DevOps ← Senior DevOps ← Cloud Architect ← SRE",
        "jobvision_slug": "devops",
        "estekhdam_slug": "",
        "irantalent_slug": "devops"
    },
    {
        "slug": "edu-devops-aws",
        "name": "مهندس AWS",
        "parent_slug": "edu-devops",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#f97316",
        "sort_order": 20,
        "skills": [
            "AWS",
            "EC2",
            "S3",
            "Lambda",
            "RDS",
            "CloudFormation",
            "ECS",
            "EKS",
            "IAM",
            "VPC"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "aws",
            "amazon web services"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-devops-azure",
        "name": "مهندس Azure",
        "parent_slug": "edu-devops",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#f97316",
        "sort_order": 21,
        "skills": [
            "Azure",
            "Azure DevOps",
            "AKS",
            "Azure Functions",
            "Active Directory",
            "CosmosDB"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "azure",
            "microsoft azure"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-devops-linux",
        "name": "مدیر سیستم لینوکس",
        "parent_slug": "edu-devops",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#f97316",
        "sort_order": 22,
        "skills": [
            "Linux",
            "Bash",
            "systemd",
            "Nginx",
            "Apache",
            "Postfix",
            "Dovecot",
            "SELinux",
            "IPTables"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "linux",
            "system administration",
            "sysadmin"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-ai",
        "name": "هوش مصنوعی و یادگیری ماشین",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7l10 5 10-5-10-5z\"/><path d=\"M2 17l10 5 10-5\"/><path d=\"M2 12l10 5 10-5\"/></svg>",
        "color": "#a855f7",
        "sort_order": 5,
        "skills": [
            "Python",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
            "NLP",
            "Computer Vision",
            "Deep Learning",
            "Pandas",
            "NumPy",
            "OpenCV",
            "Hugging Face",
            "LangChain",
            "LLM",
            "RAG",
            "Transformers",
            "BERT",
            "GPT",
            "PyTorch Lightning",
            "MLflow",
            "Weights & Biases"
        ],
        "positions": [
            "مهندس هوش مصنوعی",
            "AI Engineer",
            "ML Engineer",
            "Data Scientist",
            "NLP Engineer",
            "LLM Engineer",
            "Computer Vision Engineer",
            "Research Scientist"
        ],
        "keywords_fa": [
            "هوش مصنوعی",
            "یادگیری ماشین",
            "دیتا ساینس",
            "NLP",
            "تعلم عمیق",
            "بینایی ماشین"
        ],
        "keywords_en": [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "AI",
            "ML",
            "NLP",
            "LLM",
            "computer vision"
        ],
        "education": [
            "کارشناسی ارشد هوش مصنوعی",
            "دکتری ML",
            "کارشناسی مهندسی کامپیوتر"
        ],
        "certifications": [],
        "salary_range": "۲۵ - ۱۰۰ میلیون تومان",
        "career_path": "ML Research ← ML Engineer ← Senior ML ← AI Lead ← AI Director",
        "jobvision_slug": "ai",
        "estekhdam_slug": "",
        "irantalent_slug": "data-science"
    },
    {
        "slug": "edu-ai-nlp",
        "name": "مهندس NLP و پردازش زبان",
        "parent_slug": "edu-ai",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7l10 5 10-5-10-5z\"/><path d=\"M2 17l10 5 10-5\"/><path d=\"M2 12l10 5 10-5\"/></svg>",
        "color": "#a855f7",
        "sort_order": 24,
        "skills": [
            "NLP",
            "Transformers",
            "BERT",
            "GPT",
            "Hugging Face",
            "LangChain",
            "spaCy",
            "NLTK",
            "LlamaIndex",
            "Vector DB"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "nlp",
            "natural language processing",
            "transformers"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-ai-cv",
        "name": "مهندس بینایی ماشین",
        "parent_slug": "edu-ai",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7l10 5 10-5-10-5z\"/><path d=\"M2 17l10 5 10-5\"/><path d=\"M2 12l10 5 10-5\"/></svg>",
        "color": "#a855f7",
        "sort_order": 25,
        "skills": [
            "Computer Vision",
            "OpenCV",
            "YOLO",
            "PyTorch",
            "TensorFlow",
            "Object Detection",
            "Image Segmentation"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "computer vision",
            "opencv",
            "image processing"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-ai-mlops",
        "name": "MLOps",
        "parent_slug": "edu-ai",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7l10 5 10-5-10-5z\"/><path d=\"M2 17l10 5 10-5\"/><path d=\"M2 12l10 5 10-5\"/></svg>",
        "color": "#a855f7",
        "sort_order": 26,
        "skills": [
            "MLflow",
            "Kubeflow",
            "Airflow",
            "DVC",
            "Docker",
            "Kubernetes",
            "TensorRT",
            "ONNX",
            "Model Serving"
        ],
        "positions": [],
        "keywords_fa": [],
        "keywords_en": [
            "mlops",
            "ml pipeline"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-data",
        "name": "علم داده",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\"/><path d=\"M21 12c0 1.66-4 3-9 3s-9-1.34-9-3\"/><path d=\"M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5\"/></svg>",
        "color": "#14b8a6",
        "sort_order": 6,
        "skills": [
            "Python",
            "R",
            "SQL",
            "Machine Learning",
            "Statistics",
            "Pandas",
            "NumPy",
            "Matplotlib",
            "Seaborn",
            "Tableau",
            "Power BI",
            "Excel",
            "Jupyter",
            "Scikit-learn"
        ],
        "positions": [
            "داده‌پرداز",
            "Data Scientist",
            "Data Analyst",
            "BI Analyst",
            "Statistician"
        ],
        "keywords_fa": [
            "علم داده",
            "داده‌پرداز",
            "تحلیل داده",
            "بیگ‌دیتا",
            "آمار",
            "هوش تجاری"
        ],
        "keywords_en": [
            "data science",
            "data analyst",
            "big data",
            "analytics",
            "statistics",
            "BI"
        ],
        "education": [
            "کارشناسی ارشد آمار",
            "ارشد علوم داده",
            "دکتری"
        ],
        "certifications": [],
        "salary_range": "۲۰ - ۷۰ میلیون تومان",
        "career_path": "Data Analyst ← Data Scientist ← Senior Data Scientist ← Head of Data",
        "jobvision_slug": "data-science",
        "estekhdam_slug": "",
        "irantalent_slug": "data-science"
    },
    {
        "slug": "edu-dba",
        "name": "مدیریت دیتابیس",
        "parent_slug": "edu-data",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\"/><path d=\"M21 12c0 1.66-4 3-9 3s-9-1.34-9-3\"/><path d=\"M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5\"/></svg>",
        "color": "#0d9488",
        "sort_order": 1,
        "skills": [
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Redis",
            "SQL Server",
            "Elasticsearch",
            "Database Design",
            "Backup & Recovery",
            "Performance Tuning",
            "Oracle",
            "Cassandra",
            "DynamoDB"
        ],
        "positions": [
            "مدیر دیتابیس",
            "DBA",
            "Database Engineer",
            "Data Architect"
        ],
        "keywords_fa": [
            "دیتابیس",
            "DBA",
            "پایگاه داده"
        ],
        "keywords_en": [
            "database",
            "DBA",
            "postgresql",
            "mongodb",
            "oracle"
        ],
        "education": [
            "کارشناسی IT",
            "مجوز Oracle/Microsoft"
        ],
        "certifications": [],
        "salary_range": "۲۰ - ۶۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-security",
        "name": "امنیت سایبری",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z\"/></svg>",
        "color": "#dc2626",
        "sort_order": 7,
        "skills": [
            "Penetration Testing",
            "Network Security",
            "OWASP",
            "Firewall",
            "SIEM",
            "Incident Response",
            "Burp Suite",
            "Kali Linux",
            "CTF",
            "Malware Analysis",
            "Reverse Engineering",
            "Forensics",
            "Wireshark"
        ],
        "positions": [
            "متخصص امنیت",
            "Security Engineer",
            "Penetration Tester",
            "SOC Analyst",
            "Security Architect",
            "CISO",
            "Forensic Analyst"
        ],
        "keywords_fa": [
            "امنیت سایبری",
            "تست نفوذ",
            "فایروال",
            "جنگ سایبری",
            "تحقیقات امنیتی"
        ],
        "keywords_en": [
            "cybersecurity",
            "penetration testing",
            "security",
            "pentest",
            "SOC"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "مجوز CEH/OSCP"
        ],
        "certifications": [],
        "salary_range": "۲۰ - ۷۰ میلیون تومان",
        "career_path": "SOC Analyst ← Security Engineer ← Pentester ← Security Architect ← CISO",
        "jobvision_slug": "security",
        "estekhdam_slug": "",
        "irantalent_slug": "cybersecurity"
    },
    {
        "slug": "edu-qa",
        "name": "تست و تضمین کیفیت",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M9 11l3 3L22 4\"/><path d=\"M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11\"/></svg>",
        "color": "#6366f1",
        "sort_order": 8,
        "skills": [
            "Selenium",
            "Cypress",
            "Playwright",
            "Jira",
            "API Testing",
            "Performance Testing",
            "Manual Testing",
            "Test Planning",
            "SQL",
            "JMeter",
            "Load Testing",
            "ISTQB"
        ],
        "positions": [
            "تستر نرم‌افزار",
            "QA Engineer",
            "SDET",
            "Test Lead",
            "QA Manager"
        ],
        "keywords_fa": [
            "تست",
            "تضمین کیفیت",
            "QA",
            "تست نرم‌افزار",
            "اتوماسیون تست"
        ],
        "keywords_en": [
            "qa",
            "testing",
            "selenium",
            "quality assurance",
            "SDET"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "مدرک ISTQB"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۴۵ میلیون تومان",
        "career_path": "Manual Tester ← QA Engineer ← SDET ← QA Lead ← QA Manager",
        "jobvision_slug": "qa",
        "estekhdam_slug": "",
        "irantalent_slug": "qa"
    },
    {
        "slug": "edu-game",
        "name": "توسعه بازی",
        "parent_slug": "edu-eng-cs",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"6\" y1=\"11\" x2=\"10\" y2=\"11\"/><line x1=\"8\" y1=\"9\" x2=\"8\" y2=\"13\"/><line x1=\"15\" y1=\"12\" x2=\"15.01\" y2=\"12\"/><line x1=\"18\" y1=\"10\" x2=\"18.01\" y2=\"10\"/></svg>",
        "color": "#8b5cf6",
        "sort_order": 9,
        "skills": [
            "Unity",
            "Unreal Engine",
            "C#",
            "C++",
            "Blender",
            "Game Design",
            "Physics Engine",
            "3D Modeling",
            "Animation",
            "Photon",
            "Steam"
        ],
        "positions": [
            "برنامه‌نویس بازی",
            "Game Developer",
            "Unity Developer",
            "Game Designer"
        ],
        "keywords_fa": [
            "بازی",
            "گیم",
            "یونیتی",
            "آنریل",
            "طراحی بازی"
        ],
        "keywords_en": [
            "game development",
            "unity",
            "unreal engine",
            "game design"
        ],
        "education": [
            "کارشناسی مهندسی کامپیوتر",
            "گیم دیزاین"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-it",
        "name": "مهندسی فناوری اطلاعات",
        "parent_slug": "edu-eng",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"2\" y=\"2\" width=\"20\" height=\"8\" rx=\"2\"/><rect x=\"2\" y=\"14\" width=\"20\" height=\"8\" rx=\"2\"/><line x1=\"6\" y1=\"6\" x2=\"6.01\" y2=\"6\"/><line x1=\"6\" y1=\"18\" x2=\"6.01\" y2=\"18\"/></svg>",
        "color": "#0ea5e9",
        "sort_order": 2,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "فناوری اطلاعات",
            "IT"
        ],
        "keywords_en": [
            "IT",
            "information technology"
        ],
        "education": [
            "کارشناسی IT",
            "کارشناسی ارشد IT"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-it-network",
        "name": "شبکه و زیرساخت",
        "parent_slug": "edu-it",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"2\" y=\"2\" width=\"20\" height=\"8\" rx=\"2\"/><rect x=\"2\" y=\"14\" width=\"20\" height=\"8\" rx=\"2\"/><line x1=\"6\" y1=\"6\" x2=\"6.01\" y2=\"6\"/><line x1=\"6\" y1=\"18\" x2=\"6.01\" y2=\"18\"/></svg>",
        "color": "#0ea5e9",
        "sort_order": 1,
        "skills": [
            "Cisco",
            "Mikrotik",
            "Linux",
            "Windows Server",
            "Firewall",
            "TCP/IP",
            "DNS",
            "VPN",
            "VLAN",
            "BGP",
            "OSPF",
            "Juniper",
            "Fortinet",
            "Wireless",
            "Fiber Optic"
        ],
        "positions": [
            "مهندس شبکه",
            "Network Engineer",
            "Network Admin",
            "Sysadmin",
            "Wireless Engineer"
        ],
        "keywords_fa": [
            "شبکه",
            "سیسکو",
            "میکروتیک",
            "فایروال",
            "بی‌سیم"
        ],
        "keywords_en": [
            "network",
            "cisco",
            "mikrotik",
            "firewall",
            "system admin"
        ],
        "education": [
            "کارشناسی IT",
            "مجوز CCNA/CCNP"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۴۵ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "network",
        "estekhdam_slug": "",
        "irantalent_slug": "network"
    },
    {
        "slug": "edu-it-hw",
        "name": "تعمیر و پشتیبانی سخت‌افزار",
        "parent_slug": "edu-it",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#0ea5e9",
        "sort_order": 2,
        "skills": [
            "Hardware Repair",
            "PC Assembly",
            "Laptop Repair",
            "Printer",
            "Networking Hardware",
            "Windows",
            "Linux",
            "Troubleshooting"
        ],
        "positions": [
            "تکنسین سخت‌افزار",
            "Hardware Technician",
            "IT Support"
        ],
        "keywords_fa": [
            "تعمیر",
            "سخت‌افزار",
            "پشتیبانی",
            "تکنسین"
        ],
        "keywords_en": [
            "hardware",
            "repair",
            "IT support",
            "technician"
        ],
        "education": [
            "فنی حرفه‌ای",
            "مدرک کامپتیا"
        ],
        "certifications": [],
        "salary_range": "۱۰ - ۲۵ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-elec",
        "name": "مهندسی برق",
        "parent_slug": "edu-eng",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#eab308",
        "sort_order": 3,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "مهندسی برق",
            "الکترونیک",
            "قدرت",
            "کنترل"
        ],
        "keywords_en": [
            "electrical engineering",
            "electronics"
        ],
        "education": [
            "کارشناسی مهندسی برق"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-elec-embedded",
        "name": "الکترونیک و تعبیه‌شده",
        "parent_slug": "edu-elec",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#eab308",
        "sort_order": 36,
        "skills": [
            "C",
            "C++",
            "Embedded C",
            "Microcontroller",
            "PCB",
            "Arduino",
            "Raspberry Pi",
            "IoT",
            "ARM",
            "FPGA",
            "Verilog",
            "MATLAB",
            "Altium Designer"
        ],
        "positions": [
            "مهندس الکترونیک",
            "Embedded Engineer",
            "IoT Developer",
            "PCB Designer"
        ],
        "keywords_fa": [
            "الکترونیک",
            "تعبیه‌شده",
            "IoT",
            "آردوینو",
            "میکروکنترلر"
        ],
        "keywords_en": [
            "embedded",
            "electronics",
            "iot",
            "microcontroller"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-elec-power",
        "name": "برق قدرت",
        "parent_slug": "edu-elec",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#eab308",
        "sort_order": 37,
        "skills": [
            "MATLAB",
            "ETAP",
            "PSCAD",
            "Power Systems",
            "Substation",
            "Protection Relay",
            "Cable",
            "Transformer",
            "SCADA"
        ],
        "positions": [
            "مهندس برق قدرت",
            "Power Engineer",
            "Electrical Designer"
        ],
        "keywords_fa": [
            "برق قدرت",
            "زیرساخت برقی",
            "پست",
            "ترانسفورماتور"
        ],
        "keywords_en": [
            "power engineering",
            "electrical power"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-elec-control",
        "name": "مهندسی کنترل",
        "parent_slug": "edu-elec",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#eab308",
        "sort_order": 38,
        "skills": [
            "MATLAB",
            "Simulink",
            "PLC",
            "SCADA",
            "PID",
            "Control Systems",
            "Automation",
            "HMI",
            "DCS"
        ],
        "positions": [
            "مهندس کنترل",
            "Automation Engineer",
            "PLC Programmer"
        ],
        "keywords_fa": [
            "کنترل",
            "اتوماسیون",
            "PLC",
            "SCADA",
            "اینورتر"
        ],
        "keywords_en": [
            "control engineering",
            "automation",
            "PLC",
            "SCADA"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-civil",
        "name": "مهندسی عمران",
        "parent_slug": "edu-eng",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#65a30d",
        "sort_order": 4,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "مهندسی عمران",
            "ساختمان",
            "پل",
            "راه"
        ],
        "keywords_en": [
            "civil engineering",
            "construction"
        ],
        "education": [
            "کارشناسی مهندسی عمران"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-civil-struct",
        "name": "سازه و ساختمان",
        "parent_slug": "edu-civil",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#65a30d",
        "sort_order": 40,
        "skills": [
            "AutoCAD",
            "ETABS",
            "SAP2000",
            "Safe",
            "Revit",
            "BIM",
            "Concrete Design",
            "Steel Design",
            "MATLAB"
        ],
        "positions": [
            "مهندس سازه",
            "Structural Engineer",
            "طراح سازه"
        ],
        "keywords_fa": [
            "سازه",
            "بتن",
            "فولاد",
            "طراحی سازه"
        ],
        "keywords_en": [
            "structural",
            "building design",
            "BIM"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-civil-arch",
        "name": "معماری",
        "parent_slug": "edu-civil",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#65a30d",
        "sort_order": 41,
        "skills": [
            "AutoCAD",
            "Revit",
            "3ds Max",
            "SketchUp",
            "Lumion",
            "Photoshop",
            "BIM",
            "V-Ray",
            "Rhino",
            "Grasshopper"
        ],
        "positions": [
            "معمار",
            "Architect",
            "طراح معماری"
        ],
        "keywords_fa": [
            "معماری",
            "طراحی داخلی",
            "نما",
            "مجتمع"
        ],
        "keywords_en": [
            "architecture",
            "architect",
            "interior design"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-industrial",
        "name": "مهندسی صنایع",
        "parent_slug": "edu-eng",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M2 20a2 2 0 002 2h16a2 2 0 002-2V8l-7 5V8l-7 5V4a2 2 0 00-2-2H4a2 2 0 00-2 2z\"/><line x1=\"17\" y1=\"17\" x2=\"17\" y2=\"17.01\"/></svg>",
        "color": "#0891b2",
        "sort_order": 5,
        "skills": [
            "Optimization",
            "Simulation",
            "Lean Manufacturing",
            "Six Sigma",
            "ERP",
            "Supply Chain",
            "Project Management",
            "MATLAB",
            "Python",
            "Minitab",
            "SPSS"
        ],
        "positions": [
            "مهندس صنایع",
            "Industrial Engineer",
            "Process Engineer",
            "Lean Consultant"
        ],
        "keywords_fa": [
            "مهندسی صنایع",
            "بهینه‌سازی",
            "لین",
            "شش سیگما"
        ],
        "keywords_en": [
            "industrial engineering",
            "optimization",
            "lean",
            "six sigma"
        ],
        "education": [
            "کارشناسی مهندسی صنایع",
            "ارشد MBA"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "Industrial Engineer ← Process Engineer ← Lean Consultant ← Operations Director",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mech",
        "name": "مهندسی مکانیک",
        "parent_slug": "edu-eng",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#b45309",
        "sort_order": 6,
        "skills": [
            "SolidWorks",
            "CATIA",
            "AutoCAD",
            "ANSYS",
            "MATLAB",
            "CNC",
            "3D Printing",
            "Thermodynamics",
            "Fluid Mechanics",
            "CAD/CAM"
        ],
        "positions": [
            "مهندس مکانیک",
            "Mechanical Engineer",
            "Design Engineer",
            "Maintenance Engineer"
        ],
        "keywords_fa": [
            "مهندسی مکانیک",
            "طراحی مکانیکی",
            "تعمیرات صنعتی"
        ],
        "keywords_en": [
            "mechanical engineering",
            "CAD",
            "design engineer"
        ],
        "education": [
            "کارشناسی مهندسی مکانیک"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-design",
        "name": "طراحی و خلاقیت",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 19l7-7 3 3-7 7-3-3z\"/><path d=\"M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z\"/><path d=\"M2 2l7.586 7.586\"/><circle cx=\"11\" cy=\"11\" r=\"2\"/></svg>",
        "color": "#ec4899",
        "sort_order": 20,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "طراحی",
            "خلاقیت",
            "گرافیک"
        ],
        "keywords_en": [
            "design",
            "creative",
            "graphic"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-design-uiux",
        "name": "طراحی رابط و تجربه کاربری",
        "parent_slug": "edu-design",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 19l7-7 3 3-7 7-3-3z\"/><path d=\"M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z\"/><path d=\"M2 2l7.586 7.586\"/><circle cx=\"11\" cy=\"11\" r=\"2\"/></svg>",
        "color": "#f472b6",
        "sort_order": 1,
        "skills": [
            "Figma",
            "Adobe XD",
            "Sketch",
            "Prototyping",
            "Wireframing",
            "User Research",
            "A/B Testing",
            "Design Systems",
            "HTML/CSS",
            "Principle",
            "InVision",
            "Maze",
            "Hotjar"
        ],
        "positions": [
            "طراح UI/UX",
            "UX Researcher",
            "UI Designer",
            "Product Designer",
            "UX Lead"
        ],
        "keywords_fa": [
            "رابط کاربری",
            "تجربه کاربری",
            "UI",
            "UX",
            "فیگما",
            "پروداکت دیزاینر"
        ],
        "keywords_en": [
            "ui/ux",
            "user experience",
            "figma",
            "product design",
            "wireframe"
        ],
        "education": [
            "کارشناسی طراحی گرافیک",
            "ارشد HCI",
            "مدرک UX"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان",
        "career_path": "Junior Designer ← UI Designer ← UX Designer ← UX Lead ← Design Director",
        "jobvision_slug": "ui-ux",
        "estekhdam_slug": "",
        "irantalent_slug": "ui-ux-design"
    },
    {
        "slug": "edu-design-graphic",
        "name": "طراحی گرافیک",
        "parent_slug": "edu-design",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 19l7-7 3 3-7 7-3-3z\"/><path d=\"M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z\"/><path d=\"M2 2l7.586 7.586\"/><circle cx=\"11\" cy=\"11\" r=\"2\"/></svg>",
        "color": "#a855f7",
        "sort_order": 2,
        "skills": [
            "Photoshop",
            "Illustrator",
            "After Effects",
            "InDesign",
            "Premiere Pro",
            "CorelDRAW",
            "Branding",
            "Typography",
            "Lightroom",
            "Cinema 4D"
        ],
        "positions": [
            "طراح گرافیک",
            "Graphic Designer",
            "Visual Designer",
            "Art Director",
            "Brand Designer"
        ],
        "keywords_fa": [
            "طراحی گرافیک",
            "فتوشاپ",
            "ایلوستریتور",
            "برندینگ"
        ],
        "keywords_en": [
            "graphic design",
            "photoshop",
            "illustrator",
            "branding"
        ],
        "education": [
            "کارشناسی طراحی گرافیک",
            "هنر"
        ],
        "certifications": [],
        "salary_range": "۱۰ - ۳۵ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "graphic-design",
        "estekhdam_slug": "",
        "irantalent_slug": "graphic-design"
    },
    {
        "slug": "edu-mgmt",
        "name": "مدیریت و رهبری",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
        "color": "#8b5cf6",
        "sort_order": 30,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "مدیریت",
            "رهبری",
            "مدیر پروژه"
        ],
        "keywords_en": [
            "management",
            "leadership",
            "PM"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mgmt-product",
        "name": "مدیر محصول",
        "parent_slug": "edu-mgmt",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
        "color": "#8b5cf6",
        "sort_order": 48,
        "skills": [
            "Product Strategy",
            "Roadmapping",
            "Agile",
            "Scrum",
            "User Stories",
            "A/B Testing",
            "Data Analysis",
            "Stakeholder Management",
            "Figma",
            "Jira",
            "Amplitude"
        ],
        "positions": [
            "مدیر محصول",
            "Product Manager",
            "Product Owner"
        ],
        "keywords_fa": [
            "مدیر محصول",
            "پروادکت منیجر",
            "PO"
        ],
        "keywords_en": [
            "product manager",
            "product owner",
            "PM"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۳۰ - ۱۰۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mgmt-project",
        "name": "مدیر پروژه",
        "parent_slug": "edu-mgmt",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
        "color": "#8b5cf6",
        "sort_order": 49,
        "skills": [
            "Agile",
            "Scrum",
            "Kanban",
            "Jira",
            "Risk Management",
            "Budgeting",
            "Resource Planning",
            "MS Project",
            "Primavera",
            "Stakeholder Comm."
        ],
        "positions": [
            "مدیر پروژه",
            "Project Manager",
            "Scrum Master",
            "PMO"
        ],
        "keywords_fa": [
            "مدیر پروژه",
            "اسکرام مستر",
            "آجایل",
            "PMP"
        ],
        "keywords_en": [
            "project manager",
            "scrum master",
            "agile",
            "PMP"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۲۵ - ۸۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-finance",
        "name": "مالی و حسابداری",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"/><path d=\"M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6\"/></svg>",
        "color": "#10b981",
        "sort_order": 40,
        "skills": [
            "Excel",
            "Accounting",
            "Financial Analysis",
            "Tax",
            "Audit",
            "SAP",
            "ERP",
            "Budgeting",
            "Reporting",
            "Peachtree",
            "Hesabrayan",
            "IFRS"
        ],
        "positions": [
            "حسابدار",
            "مدیر مالی",
            "Financial Analyst",
            "Accountant",
            "Audit Manager",
            "Tax Consultant"
        ],
        "keywords_fa": [
            "حسابداری",
            "مالی",
            "حسابرسی",
            "مالیات"
        ],
        "keywords_en": [
            "accounting",
            "finance",
            "audit",
            "financial analyst",
            "tax"
        ],
        "education": [
            "کارشناسی حسابداری",
            "MBA",
            "CPA"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "accounting",
        "estekhdam_slug": "",
        "irantalent_slug": "accounting"
    },
    {
        "slug": "edu-hr",
        "name": "منابع انسانی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2\"/><circle cx=\"9\" cy=\"7\" r=\"4\"/><path d=\"M23 21v-2a4 4 0 00-3-3.87\"/><path d=\"M16 3.13a4 4 0 010 7.75\"/></svg>",
        "color": "#f43f5e",
        "sort_order": 50,
        "skills": [
            "Recruiting",
            "Onboarding",
            "Payroll",
            "Labor Law",
            "Performance Review",
            "Training",
            "HRIS",
            "Organizational Design",
            "Compensation & Benefits",
            "Talent Management",
            "LinkedIn Recruiter"
        ],
        "positions": [
            "کارشناس منابع انسانی",
            "HR Manager",
            "Recruiter",
            "Talent Acquisition",
            "HRBP",
            "Training Manager"
        ],
        "keywords_fa": [
            "منابع انسانی",
            "نیروی انسانی",
            "استخدام",
            "جذب استعداد"
        ],
        "keywords_en": [
            "HR",
            "human resources",
            "recruiting",
            "talent acquisition"
        ],
        "education": [
            "کارشناسی مدیریت منابع انسانی",
            "ارشد MBA"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "hr",
        "estekhdam_slug": "",
        "irantalent_slug": "human-resources"
    },
    {
        "slug": "edu-marketing",
        "name": "بازاریابی و فروش",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M18 3a3 3 0 00-3 3v12a3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3H6a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3V6a3 3 0 00-3-3 3 3 0 00-3 3 3 3 0 003 3h12a3 3 0 003-3 3 3 0 00-3-3z\"/></svg>",
        "color": "#f97316",
        "sort_order": 60,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "بازاریابی",
            "فروش",
            "مارکتینگ"
        ],
        "keywords_en": [
            "marketing",
            "sales"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-mktg-digital",
        "name": "دیجیتال مارکتینگ",
        "parent_slug": "edu-marketing",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M18 3a3 3 0 00-3 3v12a3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3H6a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3V6a3 3 0 00-3-3 3 3 0 00-3 3 3 3 0 003 3h12a3 3 0 003-3 3 3 0 00-3-3z\"/></svg>",
        "color": "#f97316",
        "sort_order": 53,
        "skills": [
            "Google Ads",
            "Facebook Ads",
            "SEO",
            "Google Analytics",
            "Social Media",
            "Content Marketing",
            "Email Marketing",
            "A/B Testing",
            "Copywriting",
            "WordPress"
        ],
        "positions": [
            "مدیر دیجیتال مارکتینگ",
            "Digital Marketer",
            "SEO Specialist",
            "Content Marketer"
        ],
        "keywords_fa": [
            "دیجیتال مارکتینگ",
            "سئو",
            "تبلیغات گوگل",
            "بازاریابی محتوایی",
            "گوگل ادز"
        ],
        "keywords_en": [
            "digital marketing",
            "seo",
            "google ads",
            "content marketing"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۱۵ - ۵۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "digital-marketing",
        "estekhdam_slug": "",
        "irantalent_slug": "digital-marketing"
    },
    {
        "slug": "edu-mktg-sales",
        "name": "فروش و توسعه کسب‌وکار",
        "parent_slug": "edu-marketing",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M18 3a3 3 0 00-3 3v12a3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3H6a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3V6a3 3 0 00-3-3 3 3 0 00-3 3 3 3 0 003 3h12a3 3 0 003-3 3 3 0 00-3-3z\"/></svg>",
        "color": "#f97316",
        "sort_order": 54,
        "skills": [
            "CRM",
            "B2B Sales",
            "Negotiation",
            "Business Development",
            "Cold Calling",
            "Account Management",
            "Sales Funnel",
            "HubSpot",
            "Salesforce"
        ],
        "positions": [
            "کارشناس فروش",
            "Sales Manager",
            "Business Development",
            "Account Manager"
        ],
        "keywords_fa": [
            "فروش",
            "توسعه کسب‌وکار",
            "B2B",
            "بیزینس دلوپمنت"
        ],
        "keywords_en": [
            "sales",
            "business development",
            "B2B",
            "account manager"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۱۰ - ۶۰ میلیون تومان (با پورسانت)",
        "career_path": "",
        "jobvision_slug": "sales",
        "estekhdam_slug": "",
        "irantalent_slug": "sales"
    },
    {
        "slug": "edu-mktg-brand",
        "name": "مدیریت برند",
        "parent_slug": "edu-marketing",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M18 3a3 3 0 00-3 3v12a3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3H6a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3V6a3 3 0 00-3-3 3 3 0 00-3 3 3 3 0 003 3h12a3 3 0 003-3 3 3 0 00-3-3z\"/></svg>",
        "color": "#f97316",
        "sort_order": 55,
        "skills": [
            "Brand Strategy",
            "Market Research",
            "Consumer Insights",
            "PR",
            "Social Media Management",
            "Event Management",
            "Influencer Marketing"
        ],
        "positions": [
            "مدیر برند",
            "Brand Manager",
            "PR Manager",
            "Event Manager"
        ],
        "keywords_fa": [
            "برند",
            "برندینگ",
            "روابط عمومی",
            "PR"
        ],
        "keywords_en": [
            "brand management",
            "branding",
            "PR"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "۲۰ - ۶۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-content",
        "name": "تولید محتوا",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z\"/><polyline points=\"14 2 14 8 20 8\"/><line x1=\"16\" y1=\"13\" x2=\"8\" y2=\"13\"/><line x1=\"16\" y1=\"17\" x2=\"8\" y2=\"17\"/></svg>",
        "color": "#f97316",
        "sort_order": 70,
        "skills": [
            "Copywriting",
            "SEO Writing",
            "Social Media",
            "WordPress",
            "Video Editing",
            "Photography",
            "Canva",
            "Content Strategy",
            "Adobe Premiere",
            "After Effects",
            "DaVinci Resolve"
        ],
        "positions": [
            "تولیدکننده محتوا",
            "Content Writer",
            "Copywriter",
            "Content Manager",
            "Video Producer",
            "Social Media Manager"
        ],
        "keywords_fa": [
            "تولید محتوا",
            "نویسندگی",
            "کپی‌رایتینگ",
            "ویدیو"
        ],
        "keywords_en": [
            "content writing",
            "copywriting",
            "content marketing",
            "video production"
        ],
        "education": [
            "کارشناسی ارتباطات",
            "مدرک مرتبط"
        ],
        "certifications": [],
        "salary_range": "۸ - ۳۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-legal",
        "name": "حقوق و حقوقی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7v10l10 5 10-5V7L12 2z\"/><path d=\"M12 22V12\"/><path d=\"M22 7L12 12 2 7\"/></svg>",
        "color": "#64748b",
        "sort_order": 80,
        "skills": [
            "Legal Research",
            "Contract Drafting",
            "Litigation",
            "Corporate Law",
            "Labor Law",
            "IP Law",
            "Legal Writing",
            "Arbitration"
        ],
        "positions": [
            "وکیل",
            "مشاور حقوقی",
            "Legal Counsel",
            "Judge",
            "Notary",
            "Contract Specialist"
        ],
        "keywords_fa": [
            "وکیل",
            "حقوق",
            "قانون",
            "دادگستری",
            "مشاوره حقوقی"
        ],
        "keywords_en": [
            "lawyer",
            "legal",
            "attorney",
            "legal counsel"
        ],
        "education": [
            "کارشناسی حقوق",
            "کارشناسی ارشد",
            "دانشجوی دکتری حقوق"
        ],
        "certifications": [],
        "salary_range": "۱۵ - ۶۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-medical",
        "name": "پزشکی و سلامت",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 12h-4l-3 9L9 3l-3 9H2\"/></svg>",
        "color": "#dc2626",
        "sort_order": 90,
        "skills": [
            "Clinical Medicine",
            "Diagnostics",
            "Patient Care",
            "Medical Records",
            "HIPAA",
            "EHR",
            "Medical Research"
        ],
        "positions": [
            "پزشک",
            "Doctor",
            "General Practitioner",
            "Specialist",
            "Surgeon",
            "Medical Researcher"
        ],
        "keywords_fa": [
            "پزشک",
            "دکتر",
            "طب",
            "بیمارستان",
            "درمان"
        ],
        "keywords_en": [
            "doctor",
            "physician",
            "medical",
            "healthcare",
            "hospital"
        ],
        "education": [
            "دکتری پزشکی",
            "فارغ‌التحصیل پزشکی"
        ],
        "certifications": [],
        "salary_range": "۳۰ - ۱۰۰+ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-pharma",
        "name": "داروسازی",
        "parent_slug": "edu-medical",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 12h-4l-3 9L9 3l-3 9H2\"/></svg>",
        "color": "#059669",
        "sort_order": 1,
        "skills": [
            "Pharmacology",
            "Clinical Trials",
            "Drug Development",
            "GMP",
            "Quality Control",
            "Regulatory Affairs",
            "HPLC",
            "Spectroscopy"
        ],
        "positions": [
            "داروساز",
            "Pharmacist",
            "Clinical Research Associate",
            "Regulatory Affairs Specialist",
            "QC Manager"
        ],
        "keywords_fa": [
            "داروسازی",
            "دارو",
            "صنعت دارو"
        ],
        "keywords_en": [
            "pharmacy",
            "pharmaceutical",
            "drug development"
        ],
        "education": [
            "دکتری داروسازی",
            "فارغ‌التحصیل داروسازی"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-nursing",
        "name": "پرستاری",
        "parent_slug": "edu-medical",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 12h-4l-3 9L9 3l-3 9H2\"/></svg>",
        "color": "#0891b2",
        "sort_order": 2,
        "skills": [
            "Patient Care",
            "Medical Records",
            "Vital Signs",
            "Medication Administration",
            "Wound Care",
            "CPR",
            "Infection Control"
        ],
        "positions": [
            "پرستار",
            "Nurse",
            "Head Nurse",
            "Nurse Manager"
        ],
        "keywords_fa": [
            "پرستار",
            "پرستاری",
            "بیمارستان"
        ],
        "keywords_en": [
            "nurse",
            "nursing",
            "healthcare"
        ],
        "education": [
            "کارشناسی پرستاری",
            "فارغ‌التحصیل پرستاری"
        ],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "edu-teaching",
        "name": "آموزش و تدریس",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z\"/><path d=\"M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z\"/></svg>",
        "color": "#2563eb",
        "sort_order": 100,
        "skills": [
            "Teaching",
            "Curriculum Development",
            "E-Learning",
            "Moodle",
            "PowerPoint",
            "Classroom Management",
            "Assessment",
            "Educational Technology",
            "LMS"
        ],
        "positions": [
            "معلم",
            "استاد",
            "Teacher",
            "Professor",
            "Instructional Designer",
            "E-Learning Developer",
            "Tutor"
        ],
        "keywords_fa": [
            "آموزش",
            "تدریس",
            "معلم",
            "استاد",
            "آموزش الکترونیک"
        ],
        "keywords_en": [
            "teaching",
            "education",
            "teacher",
            "professor",
            "e-learning"
        ],
        "education": [
            "کارشناسی آموزش",
            "کارشناسی ارشد آموزش",
            "دکتری"
        ],
        "certifications": [],
        "salary_range": "۸ - ۳۰ میلیون تومان",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-prog",
        "name": "زبان‌های برنامه‌نویسی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#6366f1",
        "sort_order": 100,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "برنامه‌نویسی",
            "کدنویسی"
        ],
        "keywords_en": [
            "programming",
            "coding"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-prog-python",
        "name": "پایتون",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#22c55e",
        "sort_order": 1,
        "skills": [
            "Python",
            "Django",
            "Flask",
            "FastAPI",
            "Pandas",
            "NumPy",
            "Pytest"
        ],
        "positions": [
            "Python Developer",
            "Backend Developer",
            "Data Scientist",
            "ML Engineer"
        ],
        "keywords_fa": [
            "پایتون"
        ],
        "keywords_en": [
            "python",
            "django",
            "flask"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "python",
        "estekhdam_slug": "",
        "irantalent_slug": "python"
    },
    {
        "slug": "sk-prog-js",
        "name": "جاوا اسکریپت و تایپ‌اسکریپت",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><line x1=\"3\" y1=\"9\" x2=\"21\" y2=\"9\"/><line x1=\"9\" y1=\"21\" x2=\"9\" y2=\"9\"/></svg>",
        "color": "#eab308",
        "sort_order": 2,
        "skills": [
            "JavaScript",
            "TypeScript",
            "Node.js",
            "React",
            "Vue.js",
            "Next.js"
        ],
        "positions": [
            "Frontend Developer",
            "Full Stack Developer",
            "Node Developer"
        ],
        "keywords_fa": [
            "جاوا اسکریپت"
        ],
        "keywords_en": [
            "javascript",
            "typescript",
            "node.js"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-prog-java",
        "name": "جاوا",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#ef4444",
        "sort_order": 3,
        "skills": [
            "Java",
            "Spring Boot",
            "Maven",
            "Hibernate"
        ],
        "positions": [
            "Java Developer",
            "Backend Engineer"
        ],
        "keywords_fa": [
            "جاوا"
        ],
        "keywords_en": [
            "java",
            "spring"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "java",
        "estekhdam_slug": "",
        "irantalent_slug": "java"
    },
    {
        "slug": "sk-prog-csharp",
        "name": "سی‌شارپ و دات‌نت",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#7c3aed",
        "sort_order": 4,
        "skills": [
            "C#",
            ".NET",
            "ASP.NET",
            "Blazor",
            "Entity Framework"
        ],
        "positions": [
            ".NET Developer",
            "C# Developer"
        ],
        "keywords_fa": [
            "سی‌شارپ",
            "دات نت"
        ],
        "keywords_en": [
            "c#",
            ".net"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "csharp",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-prog-php",
        "name": "پی‌اچ‌پی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
        "color": "#6366f1",
        "sort_order": 5,
        "skills": [
            "PHP",
            "Laravel",
            "WordPress",
            "MySQL"
        ],
        "positions": [
            "PHP Developer",
            "Laravel Developer"
        ],
        "keywords_fa": [
            "پی‌اچ‌پی"
        ],
        "keywords_en": [
            "php",
            "laravel"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-prog-mobile-lang",
        "name": "کاتلین و سوئیفت",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"5\" y=\"2\" width=\"14\" height=\"20\" rx=\"2\"/><line x1=\"12\" y1=\"18\" x2=\"12.01\" y2=\"18\"/></svg>",
        "color": "#ec4899",
        "sort_order": 6,
        "skills": [
            "Kotlin",
            "Swift",
            "Android SDK",
            "iOS SDK"
        ],
        "positions": [
            "Android Developer",
            "iOS Developer"
        ],
        "keywords_fa": [
            "کاتلین",
            "سوئیفت"
        ],
        "keywords_en": [
            "kotlin",
            "swift",
            "android",
            "ios"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-cloud",
        "name": "ابر و داوآپس",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#f97316",
        "sort_order": 110,
        "skills": [
            "Docker",
            "Kubernetes",
            "AWS",
            "Azure",
            "GCP",
            "Terraform",
            "CI/CD"
        ],
        "positions": [
            "DevOps Engineer",
            "Cloud Engineer",
            "SRE"
        ],
        "keywords_fa": [
            "داوآپس",
            "ابر",
            "کلاود"
        ],
        "keywords_en": [
            "devops",
            "cloud",
            "aws",
            "docker",
            "kubernetes"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "devops",
        "estekhdam_slug": "",
        "irantalent_slug": "devops"
    },
    {
        "slug": "sk-ai",
        "name": "هوش مصنوعی و یادگیری ماشین",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 2L2 7l10 5 10-5-10-5z\"/><path d=\"M2 17l10 5 10-5\"/><path d=\"M2 12l10 5 10-5\"/></svg>",
        "color": "#a855f7",
        "sort_order": 120,
        "skills": [
            "Machine Learning",
            "Deep Learning",
            "NLP",
            "LLM",
            "TensorFlow",
            "PyTorch"
        ],
        "positions": [
            "AI Engineer",
            "ML Engineer",
            "Data Scientist"
        ],
        "keywords_fa": [
            "هوش مصنوعی",
            "یادگیری ماشین"
        ],
        "keywords_en": [
            "AI",
            "ML",
            "deep learning",
            "NLP"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "ai",
        "estekhdam_slug": "",
        "irantalent_slug": "data-science"
    },
    {
        "slug": "sk-db",
        "name": "دیتابیس و ذخیره‌سازی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\"/><path d=\"M21 12c0 1.66-4 3-9 3s-9-1.34-9-3\"/><path d=\"M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5\"/></svg>",
        "color": "#14b8a6",
        "sort_order": 130,
        "skills": [
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Redis",
            "Elasticsearch",
            "SQL Server"
        ],
        "positions": [
            "DBA",
            "Database Engineer",
            "Backend Developer"
        ],
        "keywords_fa": [
            "دیتابیس",
            "پایگاه داده"
        ],
        "keywords_en": [
            "database",
            "SQL",
            "postgresql",
            "mongodb"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-security",
        "name": "امنیت و شبکه",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z\"/></svg>",
        "color": "#dc2626",
        "sort_order": 140,
        "skills": [
            "Penetration Testing",
            "Network Security",
            "Firewall",
            "Cisco",
            "Linux"
        ],
        "positions": [
            "Security Engineer",
            "Pentester",
            "Network Engineer"
        ],
        "keywords_fa": [
            "امنیت",
            "شبکه",
            "تست نفوذ"
        ],
        "keywords_en": [
            "security",
            "network",
            "penetration testing"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-frontend",
        "name": "فرانت‌اند و وب",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><line x1=\"3\" y1=\"9\" x2=\"21\" y2=\"9\"/><line x1=\"9\" y1=\"21\" x2=\"9\" y2=\"9\"/></svg>",
        "color": "#f59e0b",
        "sort_order": 150,
        "skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Vue.js",
            "Tailwind CSS",
            "SASS",
            "Next.js"
        ],
        "positions": [
            "Frontend Developer",
            "Web Developer"
        ],
        "keywords_fa": [
            "فرانت‌اند",
            "وب",
            "CSS",
            "HTML"
        ],
        "keywords_en": [
            "frontend",
            "web",
            "react",
            "vue"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "frontend",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-design-tools",
        "name": "ابزارهای طراحی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M12 19l7-7 3 3-7 7-3-3z\"/><path d=\"M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z\"/><path d=\"M2 2l7.586 7.586\"/><circle cx=\"11\" cy=\"11\" r=\"2\"/></svg>",
        "color": "#ec4899",
        "sort_order": 160,
        "skills": [
            "Figma",
            "Photoshop",
            "Illustrator",
            "After Effects",
            "Premiere Pro",
            "Sketch",
            "Adobe XD"
        ],
        "positions": [
            "UI/UX Designer",
            "Graphic Designer",
            "Video Editor"
        ],
        "keywords_fa": [
            "فیگما",
            "فتوشاپ",
            "ایلوستریتور"
        ],
        "keywords_en": [
            "figma",
            "photoshop",
            "illustrator"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "sk-data-tools",
        "name": "ابزارهای تحلیل داده",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\"/><path d=\"M21 12c0 1.66-4 3-9 3s-9-1.34-9-3\"/><path d=\"M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5\"/></svg>",
        "color": "#14b8a6",
        "sort_order": 170,
        "skills": [
            "Excel",
            "Tableau",
            "Power BI",
            "SPSS",
            "Python",
            "R",
            "SQL",
            "Pandas",
            "Matplotlib"
        ],
        "positions": [
            "Data Analyst",
            "BI Analyst",
            "Business Analyst"
        ],
        "keywords_fa": [
            "اکسل",
            "تبلو",
            "پاور بی‌آی"
        ],
        "keywords_en": [
            "excel",
            "tableau",
            "power bi",
            "data analysis"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-it",
        "name": "صنعت فناوری اطلاعات و نرم‌افزار",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#6366f1",
        "sort_order": 200,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "شرکت IT",
            "شرکت نرم‌افزاری",
            "استارتاپ",
            "فناوری"
        ],
        "keywords_en": [
            "IT company",
            "software company",
            "startup",
            "tech"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-it-dev",
        "name": "توسعه و مهندسی محصول",
        "parent_slug": "wh-it",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#6366f1",
        "sort_order": 1,
        "skills": [],
        "positions": [
            "Senior Developer",
            "Tech Lead",
            "Software Architect",
            "Principal Engineer",
            "Staff Engineer"
        ],
        "keywords_fa": [
            "تیم فنی",
            "تیم توسعه",
            "تیم مهندسی",
            "C level"
        ],
        "keywords_en": [
            "engineering",
            "development team",
            "tech lead"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-it-qa",
        "name": "کنترل کیفیت نرم‌افزار",
        "parent_slug": "wh-it",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#6366f1",
        "sort_order": 2,
        "skills": [],
        "positions": [
            "QA Lead",
            "SDET Lead",
            "Test Manager",
            "QA Director"
        ],
        "keywords_fa": [
            "تیم QA",
            "تیم تست",
            "تیم کیفیت"
        ],
        "keywords_en": [
            "QA team",
            "testing team",
            "quality"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-it-product",
        "name": "مدیریت محصول",
        "parent_slug": "wh-it",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#6366f1",
        "sort_order": 3,
        "skills": [],
        "positions": [
            "CPO",
            "VP Product",
            "Group Product Manager",
            "Head of Product"
        ],
        "keywords_fa": [
            "تیم محصول",
            "دپارتمان محصول"
        ],
        "keywords_en": [
            "product team",
            "product department"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-it-ops",
        "name": "عمليات و زیرساخت",
        "parent_slug": "wh-it",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#6366f1",
        "sort_order": 4,
        "skills": [],
        "positions": [
            "CTO",
            "VP Engineering",
            "Head of Infrastructure",
            "DevOps Manager"
        ],
        "keywords_fa": [
            "تیم داوآپس",
            "زیرساخت",
            "سیستم"
        ],
        "keywords_en": [
            "operations",
            "infrastructure",
            "devops team"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-bank",
        "name": "بانکداری و بیمه",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"/><path d=\"M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6\"/></svg>",
        "color": "#10b981",
        "sort_order": 210,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "بانک",
            "بیمه",
            "مالی",
            "نقدینگی"
        ],
        "keywords_en": [
            "banking",
            "insurance",
            "finance",
            "fintech"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-bank-retail",
        "name": "بانکداری خرد",
        "parent_slug": "wh-bank",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"/><path d=\"M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6\"/></svg>",
        "color": "#10b981",
        "sort_order": 6,
        "skills": [],
        "positions": [
            "Branch Manager",
            "Relationship Manager",
            "Loan Officer",
            "Teller"
        ],
        "keywords_fa": [
            "شعبه",
            "وام",
            "سپرده",
            "کارت"
        ],
        "keywords_en": [
            "retail banking",
            "branch",
            "loan"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-bank-corp",
        "name": "بانکداری شرکتی",
        "parent_slug": "wh-bank",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"/><path d=\"M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6\"/></svg>",
        "color": "#10b981",
        "sort_order": 7,
        "skills": [],
        "positions": [
            "Corporate Banker",
            "Trade Finance",
            "Treasury Analyst",
            "Risk Manager"
        ],
        "keywords_fa": [
            "شرکتی",
            "خزانه",
            "ریسک",
            "اعتبارات"
        ],
        "keywords_en": [
            "corporate banking",
            "treasury",
            "risk"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-bank-it",
        "name": "فناوری مالی",
        "parent_slug": "wh-bank",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"/><path d=\"M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6\"/></svg>",
        "color": "#10b981",
        "sort_order": 8,
        "skills": [],
        "positions": [
            "Fintech Developer",
            "Payment Systems Engineer",
            "Digital Banking PM"
        ],
        "keywords_fa": [
            "فین‌تک",
            "پرداخت الکترونیک",
            "بانکداری دیجیتال"
        ],
        "keywords_en": [
            "fintech",
            "payment",
            "digital banking"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-insurance",
        "name": "بیمه",
        "parent_slug": "wh-bank",
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"23\"/><path d=\"M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6\"/></svg>",
        "color": "#10b981",
        "sort_order": 9,
        "skills": [],
        "positions": [
            "Actuary",
            "Underwriter",
            "Claims Manager",
            "Insurance Broker"
        ],
        "keywords_fa": [
            "بیمه",
            "عمر",
            "خسارت",
            "ادعای بیمه"
        ],
        "keywords_en": [
            "insurance",
            "actuary",
            "claims"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-ecom",
        "name": "فروشگاه‌های اینترنتی و خرده‌فروشی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><polyline points=\"23 6 13.5 15.5 8.5 10.5 1 18\"/><polyline points=\"17 6 23 6 23 12\"/></svg>",
        "color": "#f59e0b",
        "sort_order": 220,
        "skills": [
            "Shopify",
            "WooCommerce",
            "Magento",
            "Inventory Management",
            "Supply Chain",
            "Last Mile",
            "Fulfillment",
            "CRM"
        ],
        "positions": [
            "مدیر فروشگاه آنلاین",
            "E-Commerce Manager",
            "Operations Manager",
            "Category Manager"
        ],
        "keywords_fa": [
            "فروشگاه آنلاین",
            "ای‌کامرس",
            "خرده‌فروشی",
            "دیجی‌کالا",
            "بامیلو"
        ],
        "keywords_en": [
            "e-commerce",
            "online store",
            "retail",
            "shopify",
            "marketplace"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-factory",
        "name": "صنعت تولید و کارخانه",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M2 20a2 2 0 002 2h16a2 2 0 002-2V8l-7 5V8l-7 5V4a2 2 0 00-2-2H4a2 2 0 00-2 2z\"/><line x1=\"17\" y1=\"17\" x2=\"17\" y2=\"17.01\"/></svg>",
        "color": "#b45309",
        "sort_order": 230,
        "skills": [
            "Production Planning",
            "Quality Control",
            "Lean Manufacturing",
            "ERP",
            "Supply Chain",
            "Safety Management",
            "ISO"
        ],
        "positions": [
            "مدیر تولید",
            "Production Manager",
            "Factory Manager",
            "Quality Manager",
            "Plant Manager"
        ],
        "keywords_fa": [
            "تولید",
            "کارخانه",
            "صنعت",
            "خط تولید",
            "کارگاه"
        ],
        "keywords_en": [
            "manufacturing",
            "production",
            "factory",
            "plant"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-construct",
        "name": "ساختمان و عمران",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#65a30d",
        "sort_order": 240,
        "skills": [
            "Project Management",
            "AutoCAD",
            "Revit",
            "BIM",
            "Site Management",
            "Safety",
            "Estimation"
        ],
        "positions": [
            "مدیر پروژه ساختمان",
            "Site Engineer",
            "Construction Manager",
            "Project Director"
        ],
        "keywords_fa": [
            "ساختمان",
            "عمران",
            "پروژه ساختمانی",
            "کارگاه ساختمانی"
        ],
        "keywords_en": [
            "construction",
            "building",
            "civil works",
            "site management"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-health",
        "name": "بهداشت و درمان",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 12h-4l-3 9L9 3l-3 9H2\"/></svg>",
        "color": "#dc2626",
        "sort_order": 250,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "بیمارستان",
            "درمانگاه",
            "کلینیک",
            "آزمایشگاه",
            "داروخانه"
        ],
        "keywords_en": [
            "hospital",
            "clinic",
            "healthcare",
            "pharmacy",
            "lab"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-telecom",
        "name": "مخابرات و ارتباطات",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z\"/></svg>",
        "color": "#0ea5e9",
        "sort_order": 260,
        "skills": [
            "Telecom Infrastructure",
            "5G",
            "Fiber Optic",
            "Networking",
            "OSS/BSS",
            "RF Engineering",
            "Tower Management"
        ],
        "positions": [
            "مهندس مخابرات",
            "Telecom Engineer",
            "Network Planner",
            "RF Engineer"
        ],
        "keywords_fa": [
            "مخابرات",
            "اینترنت",
            "سیم‌کارت",
            "فیبر نوری",
            "برج"
        ],
        "keywords_en": [
            "telecom",
            "telecommunications",
            "ISP",
            "mobile operator"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-oil",
        "name": "نفت، گاز و پتروشیمی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z\"/></svg>",
        "color": "#78350f",
        "sort_order": 270,
        "skills": [
            "Process Engineering",
            "HSE",
            "Pipeline",
            "Refining",
            "Petrochemicals",
            "SCADA",
            "Instrumentation",
            "Mechanical"
        ],
        "positions": [
            "مهندس نفت",
            "Process Engineer",
            "HSE Manager",
            "Plant Manager",
            "Project Engineer"
        ],
        "keywords_fa": [
            "نفت",
            "گاز",
            "پتروشیمی",
            "پالایشگاه",
            "میدان نفتی"
        ],
        "keywords_en": [
            "oil",
            "gas",
            "petrochemical",
            "refining",
            "upstream",
            "downstream"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-transport",
        "name": "حمل و نقل و لجستیک",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"1\" y=\"3\" width=\"15\" height=\"13\"/><polygon points=\"16 8 20 8 23 11 23 16 16 16 16 8\"/><circle cx=\"5.5\" cy=\"18.5\" r=\"2.5\"/><circle cx=\"18.5\" cy=\"18.5\" r=\"2.5\"/></svg>",
        "color": "#0891b2",
        "sort_order": 280,
        "skills": [
            "Supply Chain",
            "Warehousing",
            "Fleet Management",
            "Customs",
            "Freight",
            "Last Mile",
            "ERP",
            "Routing"
        ],
        "positions": [
            "مدیر لجستیک",
            "Logistics Manager",
            "Supply Chain Manager",
            "Warehouse Manager",
            "Fleet Manager"
        ],
        "keywords_fa": [
            "لجستیک",
            "حمل و نقل",
            "انبار",
            "توزیع",
            "باربری"
        ],
        "keywords_en": [
            "logistics",
            "transportation",
            "supply chain",
            "warehousing",
            "freight"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-media",
        "name": "رسانه و تبلیغات",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z\"/><polyline points=\"14 2 14 8 20 8\"/><line x1=\"16\" y1=\"13\" x2=\"8\" y2=\"13\"/><line x1=\"16\" y1=\"17\" x2=\"8\" y2=\"17\"/></svg>",
        "color": "#f97316",
        "sort_order": 290,
        "skills": [
            "Content Strategy",
            "Social Media",
            "Video Production",
            "Photography",
            "Journalism",
            "SEO",
            "Google Ads",
            "Programmatic"
        ],
        "positions": [
            "مدیر رسانه",
            "Media Director",
            "Content Director",
            "Creative Director",
            "Journalist"
        ],
        "keywords_fa": [
            "رسانه",
            "تبلیغات",
            "آژانس تبلیغاتی",
            "خبرنگاری",
            "محتوا"
        ],
        "keywords_en": [
            "media",
            "advertising",
            "agency",
            "journalism",
            "content"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    },
    {
        "slug": "wh-gov",
        "name": "دولت و بخش عمومی",
        "parent_slug": null,
        "icon_svg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><rect x=\"4\" y=\"2\" width=\"16\" height=\"20\" rx=\"2\"/><path d=\"M9 22v-4h6v4\"/><path d=\"M8 6h.01\"/><path d=\"M16 6h.01\"/><path d=\"M12 6h.01\"/><path d=\"M12 10h.01\"/><path d=\"M12 14h.01\"/><path d=\"M16 10h.01\"/><path d=\"M16 14h.01\"/><path d=\"M8 10h.01\"/><path d=\"M8 14h.01\"/></svg>",
        "color": "#64748b",
        "sort_order": 300,
        "skills": [],
        "positions": [],
        "keywords_fa": [
            "دولت",
            "وزارتخانه",
            "اداری",
            "بخش عمومی"
        ],
        "keywords_en": [
            "government",
            "public sector",
            "ministry",
            "civil service"
        ],
        "education": [],
        "certifications": [],
        "salary_range": "",
        "career_path": "",
        "jobvision_slug": "",
        "estekhdam_slug": "",
        "irantalent_slug": ""
    }
]



class Command(BaseCommand):
    help = 'Seed JobCategory tree (education + skills + work-history). Deletes old data first.'

    def handle(self, *args, **options):
        self.stdout.write('Deleting all existing categories...')
        JobCategory.objects.all().delete()

        created = {}
        count = 0

        for cat_data in ALL_CATEGORIES:
            parent = None
            if cat_data['parent_slug'] and cat_data['parent_slug'] in created:
                parent = created[cat_data['parent_slug']]

            obj, is_new = JobCategory.objects.update_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'parent': parent,
                    'icon_svg': cat_data['icon_svg'],
                    'color': cat_data['color'],
                    'sort_order': cat_data['sort_order'],
                    'skills': cat_data['skills'],
                    'positions': cat_data['positions'],
                    'keywords_fa': cat_data['keywords_fa'],
                    'keywords_en': cat_data['keywords_en'],
                    'education': cat_data['education'],
                    'certifications': cat_data['certifications'],
                    'salary_range': cat_data['salary_range'],
                    'career_path': cat_data['career_path'],
                    'jobvision_slug': cat_data['jobvision_slug'],
                    'estekhdam_slug': cat_data['estekhdam_slug'],
                    'irantalent_slug': cat_data['irantalent_slug'],
                    'is_active': True,
                },
            )
            created[cat_data['slug']] = obj
            count += 1

        roots = JobCategory.objects.filter(parent=None).count()
        total = JobCategory.objects.count()
        max_depth = 0
        for cat in JobCategory.objects.all():
            d = len(cat.get_full_path().split(' > '))
            if d > max_depth:
                max_depth = d

        self.stdout.write(self.style.SUCCESS(
            f'Done! {count} categories seeded ({roots} roots, {total} total, max depth={max_depth})'
        ))
