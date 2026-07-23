"""
Comprehensive job categories seed data with DUAL PARALLEL TREES:
  1. Education-based tree (تحصیلی): University majors → Specializations → Job titles → Skills
  2. Skills-based tree (مهارتی): Tech areas → Specializations → Titles → Skills

Each leaf node has platform slugs (jobvision, irantalent, estekhdam),
skills, positions, keywords, education requirements, and career paths.

Run: python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from core.models import JobCategory

ICONS = {
    'developer': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    'frontend': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
    'mobile': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>',
    'data': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    'ai': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
    'devops': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>',
    'design': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>',
    'marketing': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 3a3 3 0 00-3 3v12a3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3H6a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3V6a3 3 0 00-3-3 3 3 0 00-3 3 3 3 0 003 3h12a3 3 0 003-3 3 3 0 00-3-3z"/></svg>',
    'finance': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    'hr': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    'management': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    'network': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>',
    'security': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    'content': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    'sales': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    'medical': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'engineering': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>',
    'qa': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>',
    'game': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="6" y1="11" x2="10" y2="11"/><line x1="8" y1="9" x2="8" y2="13"/><line x1="15" y1="12" x2="15.01" y2="12"/><line x1="18" y1="10" x2="18.01" y2="10"/><path d="M17.32 5H6.68a4 4 0 00-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 2 16a3 3 0 003 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 019.828 16h4.344a2 2 0 011.414.586L17 18c.5.5 1 1 2 1a3 3 0 003-3c0-1.544-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.151A4 4 0 0017.32 5z"/></svg>',
}


def _c(slug, name, parent_slug=None, icon='developer', color='#6366f1',
       sort_order=0, skills=None, positions=None, keywords_fa=None,
       keywords_en=None, education=None, certifications=None,
       salary_range='', career_path='',
       jobvision_slug='', estekhdam_slug='', irantalent_slug=''):
    """Helper to create a category dict for seeding."""
    return {
        'slug': slug, 'name': name, 'parent_slug': parent_slug,
        'icon_svg': ICONS.get(icon, ICONS['developer']),
        'color': color, 'sort_order': sort_order,
        'skills': skills or [], 'positions': positions or [],
        'keywords_fa': keywords_fa or [], 'keywords_en': keywords_en or [],
        'education': education or [], 'certifications': certifications or [],
        'salary_range': salary_range, 'career_path': career_path,
        'jobvision_slug': jobvision_slug, 'estekhdam_slug': estekhdam_slug,
        'irantalent_slug': irantalent_slug,
    }


# ──────────────────────────────────────────────────
# TREE 1: Education-Based (درخت تحصیلی)
# University Major → Specialization → Job Title → Skills
# ──────────────────────────────────────────────────
EDUCATION_TREE = [
    # Level 1: Engineering (مهندسی)
    _c('eng', 'مهندسی', icon='engineering', color='#3b82f6', sort_order=10,
       keywords_fa=['مهندسی', 'مهندس'], keywords_en=['engineering', 'engineer'],
       education=['کارشناسی مهندسی', 'کارشناسی ارشد', 'دکتری'],
       career_path='مهندس جونیور → مهندس متخصص → مهندس ارشد → مدیر فنی → مدیر ارشد مهندسی'),

    # Level 2: Computer Engineering
    _c('eng-computer', 'مهندسی کامپیوتر', parent_slug='eng', icon='developer', color='#6366f1', sort_order=1,
       keywords_fa=['مهندسی کامپیوتر', 'مهندسی نرم‌افزار', 'مهندسی سخت‌افزار'],
       keywords_en=['computer engineering', 'software engineering', 'computer science'],
       education=['کارشناسی مهندسی کامپیوتر', 'کارشناسی ارشد نرم‌افزار'],
       career_path='برنامه‌نویس جونیور → برنامه‌نویس ارشد → معماری نرم‌افزار → CTO'),

    # Level 3: Software Engineering
    _c('eng-sw', 'مهندسی نرم‌افزار', parent_slug='eng-computer', icon='developer', color='#8b5cf6', sort_order=1,
       skills=['Python', 'Java', 'C#', 'JavaScript', 'TypeScript', 'Go', 'Rust',
               'SQL', 'Git', 'Linux', 'Docker', 'REST API', 'Microservices',
               'Object-Oriented', 'Design Patterns', 'Unit Testing', 'CI/CD'],
       positions=['برنامه‌نویس بک‌اند', 'توسعه‌دهنده نرم‌افزار', 'مهندس نرم‌افزار',
                  'Backend Developer', 'Software Engineer'],
       keywords_fa=['نرم‌افزار', 'برنامه‌نویسی', 'توسعه', 'بک‌اند', 'backend'],
       keywords_en=['software', 'programming', 'backend', 'development', 'coder'],
       education=['کارشناسی مهندسی کامپیوتر', 'کارشناسی ارشد نرم‌افزار', 'دکتری مهندسی نرم‌افزار'],
       salary_range='۱۵ - ۵۰ میلیون تومان (جونیور تا سنیور)',
       career_path='Junior Dev → Mid Dev → Senior Dev → Tech Lead → Software Architect → CTO',
       jobvision_slug='software', estekhdam_slug='software', irantalent_slug='software-engineering'),

    # Level 4: Python Backend
    _c('eng-sw-python', 'توسعه‌دهنده پایتون', parent_slug='eng-sw', icon='developer', color='#22c55e', sort_order=1,
       skills=['Python', 'Django', 'Flask', 'FastAPI', 'Celery', 'PostgreSQL',
               'Redis', 'Docker', 'REST API', 'SQLAlchemy', 'Pytest',
               'Pandas', 'Scrapy', 'gRPC'],
       positions=['برنامه‌نویس پایتون', 'توسعه‌دهنده بک‌اند پایتون',
                  'Python Developer', 'Django Developer', 'Backend Engineer'],
       keywords_fa=['پایتون', 'جنگو', 'فلسک', 'دجانگو'],
       keywords_en=['python', 'django', 'flask', 'fastapi'],
       education=['کارشناسی مهندسی کامپیوتر', 'کارشناسی IT'],
       salary_range='۲۰ - ۶۰ میلیون تومان',
       career_path='Python Dev → Senior Python → Django Expert → Backend Architect',
       jobvision_slug='python', irantalent_slug='python'),

    # Level 4: Java Backend
    _c('eng-sw-java', 'توسعه‌دهنده جاوا', parent_slug='eng-sw', icon='developer', color='#ef4444', sort_order=2,
       skills=['Java', 'Spring Boot', 'Spring Cloud', 'Maven', 'Gradle',
               'Hibernate', 'PostgreSQL', 'Microservices', 'Kafka',
               'Redis', 'Docker', 'Kubernetes', 'Jenkins'],
       positions=['برنامه‌نویس جاوا', 'توسعه‌دهنده Spring',
                  'Java Developer', 'Backend Engineer Java'],
       keywords_fa=['جاوا', 'اسپرینگ', 'جاوا اسپرینگ'],
       keywords_en=['java', 'spring', 'spring boot'],
       education=['کارشناسی مهندسی کامپیوتر', 'کارشناسی IT'],
       salary_range='۲۰ - ۷۰ میلیون تومان',
       career_path='Java Dev → Senior Java → Spring Architect → Tech Lead',
       jobvision_slug='java', irantalent_slug='java'),

    # Level 4: .NET Backend
    _c('eng-sw-dotnet', 'توسعه‌دهنده دات‌نت', parent_slug='eng-sw', icon='developer', color='#7c3aed', sort_order=3,
       skills=['C#', '.NET Core', 'ASP.NET', 'Entity Framework', 'SQL Server',
               'Azure', 'Blazor', 'WPF', 'LINQ', 'Docker'],
       positions=['برنامه‌نویس سی‌شارپ', 'توسعه‌دهنده دات‌نت', '.NET Developer'],
       keywords_fa=['سی شارپ', 'دات نت', 'سی‌شارپ'],
       keywords_en=['c#', '.net', 'dotnet'],
       education=['کارشناسی مهندسی کامپیوتر', 'کارشناسی IT'],
       salary_range='۱۸ - ۵۵ میلیون تومان'),

    # Level 4: Node.js
    _c('eng-sw-nodejs', 'توسعه‌دهنده نود جی‌اس', parent_slug='eng-sw', icon='developer', color='#22c55e', sort_order=4,
       skills=['Node.js', 'Express', 'NestJS', 'TypeScript', 'MongoDB',
               'PostgreSQL', 'Redis', 'Socket.IO', 'Docker', 'GraphQL'],
       positions=['برنامه‌نویس نود', 'Node Developer', 'Full Stack Developer'],
       keywords_fa=['نود جی‌اس', 'نود', 'Node.js'],
       keywords_en=['nodejs', 'node.js', 'express'],
       salary_range='۱۸ - ۵۵ میلیون تومان'),

    # Level 4: PHP/Laravel
    _c('eng-sw-php', 'توسعه‌دهنده پی‌اچ‌پی', parent_slug='eng-sw', icon='developer', color='#6366f1', sort_order=5,
       skills=['PHP', 'Laravel', 'WordPress', 'MySQL', 'Redis', 'Docker',
               'Composer', 'PHPUnit', 'REST API', 'Vue.js'],
       positions=['برنامه‌نویس پی‌اچ‌پی', 'Laravel Developer'],
       keywords_fa=['پی‌اچ‌پی', 'لاراول', 'وردپرس'],
       keywords_en=['php', 'laravel', 'wordpress'],
       salary_range='۱۵ - ۴۵ میلیون تومان'),

    # Level 3: Frontend
    _c('eng-frontend', 'توسعه‌دهنده فرانت‌اند', parent_slug='eng-computer', icon='frontend', color='#f59e0b', sort_order=2,
       skills=['HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Vue.js',
               'Angular', 'Next.js', 'Nuxt.js', 'Tailwind CSS', 'SASS',
               'Webpack', 'Vite', 'Responsive Design', 'PWA'],
       positions=['طراح و توسعه‌دهنده وب', 'فرانت‌اند دولوپر', 'Frontend Developer',
                  'React Developer', 'UI Developer'],
       keywords_fa=['فرانت‌اند', 'وب', 'رابط کاربری', 'React', 'ویو'],
       keywords_en=['frontend', 'web', 'react', 'vue', 'angular', 'ui'],
       education=['کارشناسی مهندسی کامپیوتر', 'کارشناسی IT', 'مدرک معادل'],
       salary_range='۱۵ - ۵۰ میلیون تومان',
       career_path='Junior Frontend → Frontend Dev → Senior Frontend → Frontend Architect → UI/UX Tech Lead',
       jobvision_slug='frontend', irantalent_slug='frontend'),

    # Level 4: React
    _c('eng-fe-react', 'توسعه‌دهنده ریکت', parent_slug='eng-frontend', icon='frontend', color='#06b6d4', sort_order=1,
       skills=['React', 'Next.js', 'TypeScript', 'Redux', 'React Query',
               'Tailwind CSS', 'Jest', 'Cypress', 'Storybook'],
       positions=['React Developer', 'Next.js Developer', 'Frontend Engineer'],
       keywords_en=['react', 'next.js', 'redux'],
       salary_range='۲۰ - ۶۰ میلیون تومان'),

    # Level 4: Vue.js
    _c('eng-fe-vue', 'توسعه‌دهنده ویو', parent_slug='eng-frontend', icon='frontend', color='#22c55e', sort_order=2,
       skills=['Vue.js', 'Nuxt.js', 'Vuex', 'Pinia', 'Vuetify', 'TypeScript'],
       positions=['Vue Developer', 'Nuxt Developer'],
       keywords_en=['vue', 'nuxt'],
       salary_range='۱۵ - ۴۵ میلیون تومان'),

    # Level 3: Mobile Dev
    _c('eng-mobile', 'توسعه‌دهنده موبایل', parent_slug='eng-computer', icon='mobile', color='#ec4899', sort_order=3,
       skills=['Flutter', 'React Native', 'Swift', 'Kotlin', 'Dart',
               'iOS', 'Android', 'Firebase', 'REST API', 'SQLite'],
       positions:['توسعه‌دهنده موبایل', 'Mobile Developer', 'iOS Developer',
                  'Android Developer', 'Flutter Developer'],
       keywords_fa=['موبایل', 'اندروید', 'آی‌او‌اس', 'فلاتر'],
       keywords_en=['mobile', 'android', 'ios', 'flutter', 'react native'],
       education=['کارشناسی مهندسی کامپیوتر', 'کارشناسی IT'],
       salary_range='۲۰ - ۶۰ میلیون تومان',
       career_path='Junior Mobile → Mobile Dev → Senior Mobile → Mobile Tech Lead',
       jobvision_slug='mobile', irantalent_slug='mobile'),

    # Level 3: DevOps/Cloud
    _c('eng-devops', 'داوآپس و زیرساخت', parent_slug='eng-computer', icon='devops', color='#f97316', sort_order=4,
       skills=['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Linux',
               'CI/CD', 'Jenkins', 'GitHub Actions', 'Terraform', 'Ansible',
               'Prometheus', 'Grafana', 'Nginx'],
       positions=['مهندس داوآپس', 'DevOps Engineer', 'Cloud Engineer',
                  'Site Reliability Engineer', 'SRE'],
       keywords_fa=['داوآپس', 'زیرساخت', 'اکس', 'دکر', 'کوبرنیتیس'],
       keywords_en=['devops', 'cloud', 'aws', 'docker', 'kubernetes', 'sre'],
       education=['کارشناسی مهندسی کامپیوتر', 'شبکه', 'مجوز AWS/Azure'],
       salary_range='۲۵ - ۸۰ میلیون تومان',
       career_path='Sysadmin → DevOps → Senior DevOps → Cloud Architect → SRE',
       jobvision_slug='devops', irantalent_slug='devops'),

    # Level 3: AI/ML
    _c('eng-ai', 'هوش مصنوعی و یادگیری ماشین', parent_slug='eng-computer', icon='ai', color='#a855f7', sort_order=5,
       skills=['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'NLP',
               'Computer Vision', 'Deep Learning', 'Pandas', 'NumPy',
               'OpenCV', 'Hugging Face', 'LangChain', 'LLM', 'RAG'],
       positions=['مهندس هوش مصنوعی', 'AI Engineer', 'ML Engineer',
                  'Data Scientist', 'NLP Engineer', 'LLM Engineer'],
       keywords_fa=['هوش مصنوعی', 'یادگیری ماشین', 'دیتا ساینس', 'NLP', 'تعلم عمیق'],
       keywords_en=['artificial intelligence', 'machine learning', 'deep learning', 'AI', 'ML', 'NLP', 'LLM'],
       education=['کارشناسی ارشد هوش مصنوعی', 'دکتری ML', 'کارشناسی مهندسی کامپیوتر'],
       salary_range='۲۵ - ۱۰۰ میلیون تومان',
       career_path='ML Research → ML Engineer → Senior ML → AI Lead → AI Director',
       jobvision_slug='ai', irantalent_slug='data-science'),

    # Level 2: IT Engineering
    _c('eng-it', 'مهندسی فناوری اطلاعات', parent_slug='eng', icon='network', color='#0ea5e9', sort_order=2,
       keywords_fa=['فناوری اطلاعات', 'IT'], keywords_en=['IT', 'information technology'],
       education=['کارشناسی IT', 'کارشناسی ارشد IT']),

    # Level 3: Network
    _c('eng-it-network', 'شبکه و زیرساخت', parent_slug='eng-it', icon='network', color='#0ea5e9', sort_order=1,
       skills=['Cisco', 'Mikrotik', 'Linux', 'Windows Server', 'Firewall',
               'TCP/IP', 'DNS', 'VPN', 'VLAN', 'BGP', 'OSPF'],
       positions=['مهندس شبکه', 'Network Engineer', 'Network Admin', 'Sysadmin'],
       keywords_fa=['شبکه', 'سیسکو', 'میکروتیک', 'فایروال'],
       keywords_en=['network', 'cisco', 'mikrotik', 'firewall', 'system admin'],
       education=['کارشناسی IT', 'مجوز CCNA/CCNP'],
       salary_range='۱۵ - ۴۵ میلیون تومان',
       jobvision_slug='network', irantalent_slug='network'),

    # Level 2: Electrical Engineering
    _c('eng-electrical', 'مهندسی برق', parent_slug='eng', icon='engineering', color='#eab308', sort_order=3,
       keywords_fa=['مهندسی برق', 'الکترونیک'], keywords_en=['electrical engineering', 'electronics'],
       education=['کارشناسی مهندسی برق']),

    # Level 3: Embedded
    _c('eng-elec-embedded', 'الکترونیک و تعبیه‌شده', parent_slug='eng-electrical', icon='engineering', color='#eab308', sort_order=1,
       skills=['C', 'C++', 'Embedded C', 'Microcontroller', 'PCB', 'Arduino',
               'Raspberry Pi', 'IoT', 'ARM', 'FPGA', 'Verilog', 'MATLAB'],
       positions=['مهندس الکترونیک', 'Embedded Engineer', 'IoT Developer'],
       keywords_fa=['الکترونیک', 'تعبیه‌شده', 'IoT', 'آردوینو'],
       keywords_en=['embedded', 'electronics', 'iot', 'microcontroller'],
       education=['کارشناسی مهندسی برق'],
       salary_range='۱۵ - ۵۰ میلیون تومان'),

    # ── Level 1: Design (طراحی) ──
    _c('design', 'طراحی و خلاقیت', icon='design', color='#ec4899', sort_order=20,
       keywords_fa=['طراحی', 'خلاقیت', 'گرافیک'], keywords_en=['design', 'creative', 'graphic']),

    # Level 2: UI/UX
    _c('design-uiux', 'طراحی رابط و تجربه کاربری', parent_slug='design', icon='design', color='#f472b6', sort_order=1,
       skills=['Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'Wireframing',
               'User Research', 'A/B Testing', 'Design Systems', 'HTML/CSS'],
       positions=['طراح UI/UX', 'UX Researcher', 'UI Designer', 'Product Designer'],
       keywords_fa=['رابط کاربری', 'تجربه کاربری', 'UI', 'UX', 'فیگما'],
       keywords_en=['ui/ux', 'user experience', 'figma', 'product design'],
       education=['کارشناسی طراحی گرافیک', 'ارشد HCI', 'مدرک UX'],
       salary_range='۱۵ - ۵۰ میلیون تومان',
       career_path='Junior Designer → UI Designer → UX Designer → UX Lead → Design Director',
       jobvision_slug='ui-ux', irantalent_slug='ui-ux-design'),

    # Level 2: Graphic Design
    _c('design-graphic', 'طراحی گرافیک', parent_slug='design', icon='design', color='#a855f7', sort_order=2,
       skills=['Photoshop', 'Illustrator', 'After Effects', 'InDesign',
               'Premiere Pro', 'CorelDRAW', 'Branding', 'Typography'],
       positions=['طراح گرافیک', 'Graphic Designer', 'Visual Designer', 'Art Director'],
       keywords_fa=['طراحی گرافیک', 'فتوشاپ', 'ایلوستریتور'],
       keywords_en=['graphic design', 'photoshop', 'illustrator', 'branding'],
       education=['کارشناسی طراحی گرافیک', 'هنر'],
       salary_range='۱۰ - ۳۵ میلیون تومان',
       jobvision_slug='graphic-design', irantalent_slug='graphic-design'),

    # ── Level 1: Marketing (بازاریابی) ──
    _c('marketing', 'بازاریابی و فروش', icon='marketing', color='#f97316', sort_order=30,
       keywords_fa=['بازاریابی', 'فروش', 'مارکتینگ'], keywords_en=['marketing', 'sales']),

    # Level 2: Digital Marketing
    _c('marketing-digital', 'دیجیتال مارکتینگ', parent_slug='marketing', icon='marketing', color='#fb923c', sort_order=1,
       skills=['Google Ads', 'Facebook Ads', 'SEO', 'Google Analytics',
               'Social Media', 'Content Marketing', 'Email Marketing', 'A/B Testing'],
       positions=['مدیر دیجیتال مارکتینگ', 'Digital Marketer', 'SEO Specialist', 'Content Marketer'],
       keywords_fa=['دیجیتال مارکتینگ', 'سئو', 'تبلیغات گوگل', 'بازاریابی محتوایی'],
       keywords_en=['digital marketing', 'seo', 'google ads', 'content marketing'],
       education=['کارشناسی مدیریت بازرگانی', 'مدرک گوگل', 'حوزه مرتبط'],
       salary_range='۱۵ - ۵۰ میلیون تومان',
       career_path='Digital Marketer → SEO Specialist → Digital Marketing Manager → CMO',
       jobvision_slug='digital-marketing', irantalent_slug='digital-marketing'),

    # Level 2: Sales
    _c('marketing-sales', 'فروش و توسعه کسب‌وکار', parent_slug='marketing', icon='sales', color='#f59e0b', sort_order=2,
       skills=['CRM', 'B2B Sales', 'Negotiation', 'Business Development',
               'Cold Calling', 'Account Management', 'Sales Funnel'],
       positions=['کارشناس فروش', 'Sales Manager', 'Business Development', 'Account Manager'],
       keywords_fa=['فروش', 'توسعه کسب‌وکار', 'B2B'],
       keywords_en=['sales', 'business development', 'B2B', 'account manager'],
       education=['کارشناسی مدیریت', 'MBA'],
       salary_range='۱۰ - ۶۰ میلیون تومان (با پورسانت)'),
       jobvision_slug='sales', irantalent_slug='sales'),

    # ── Level 1: Data & Analytics ──
    _c('data', 'داده و تحلیل', icon='data', color='#14b8a6', sort_order=40,
       keywords_fa=['داده', 'تحلیل', 'بیگ‌دیتا'], keywords_en=['data', 'analytics', 'big data']),

    # Level 2: Data Science
    _c('data-science', 'علم داده', parent_slug='data', icon='data', color='#14b8a6', sort_order=1,
       skills=['Python', 'R', 'SQL', 'Machine Learning', 'Statistics',
               'Pandas', 'NumPy', 'Matplotlib', 'Tableau', 'Power BI'],
       positions=['داده‌پرداز', 'Data Scientist', 'Data Analyst', 'BI Analyst'],
       keywords_fa=['علم داده', 'داده‌پرداز', 'تحلیل داده', 'بیگ‌دیتا'],
       keywords_en=['data science', 'data analyst', 'big data', 'analytics'],
       education=['کارشناسی ارشد آمار', 'ارشد علوم داده', 'دکتری'],
       salary_range='۲۰ - ۷۰ میلیون تومان',
       career_path='Data Analyst → Data Scientist → Senior Data Scientist → Head of Data',
       jobvision_slug='data-science', irantalent_slug='data-science'),

    # Level 2: Database
    _c('data-dba', 'مدیریت دیتابیس', parent_slug='data', icon='data', color='#0d9488', sort_order=2,
       skills=['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQL Server',
               'Elasticsearch', 'Database Design', 'Backup & Recovery', 'Performance Tuning'],
       positions=['مدیر دیتابیس', 'DBA', 'Database Engineer'],
       keywords_fa=['دیتابیس', 'DBA', 'پایگاه داده'],
       keywords_en=['database', 'DBA', 'postgresql', 'mongodb'],
       education=['کارشناسی IT', 'مجوز Oracle/Microsoft'],
       salary_range='۲۰ - ۶۰ میلیون تومان'),

    # ── Level 1: QA & Testing ──
    _c('qa', 'تست و تضمین کیفیت', icon='qa', color='#6366f1', sort_order=50,
       skills=['Selenium', 'Cypress', 'Playwright', 'Jira', 'API Testing',
               'Performance Testing', 'Manual Testing', 'Test Planning', 'SQL'],
       positions=['تستر نرم‌افزار', 'QA Engineer', 'SDET', 'Test Lead'],
       keywords_fa=['تست', 'تضمین کیفیت', 'QA', 'تست نرم‌افزار'],
       keywords_en=['qa', 'testing', 'selenium', 'quality assurance'],
       education=['کارشناسی مهندسی کامپیوتر', 'مدرک ISTQB'],
       salary_range='۱۵ - ۴۵ میلیون تومان',
       career_path='Manual Tester → QA Engineer → SDET → QA Lead → QA Manager',
       jobvision_slug='qa', irantalent_slug='qa'),

    # ── Level 1: Cybersecurity ──
    _c('security', 'امنیت سایبری', icon='security', color='#dc2626', sort_order=55,
       skills=['Penetration Testing', 'Network Security', 'OWASP', 'Firewall',
               'SIEM', 'Incident Response', 'Burp Suite', 'Kali Linux', 'CTF'],
       positions=['متخصص امنیت', 'Security Engineer', 'Penetration Tester', 'SOC Analyst'],
       keywords_fa=['امنیت سایبری', 'تست نفوذ', 'فایروال'],
       keywords_en=['cybersecurity', 'penetration testing', 'security', 'pentest'],
       education=['کارشناسی مهندسی کامپیوتر', 'مجوز CEH/OSCP'],
       salary_range='۲۰ - ۷۰ میلیون تومان',
       career_path='SOC Analyst → Security Engineer → Pentester → Security Architect → CISO',
       jobvision_slug='security', irantalent_slug='cybersecurity'),

    # ── Level 1: Management (مدیریت) ──
    _c('management', 'مدیریت و رهبری', icon='management', color='#8b5cf6', sort_order=60,
       keywords_fa=['مدیریت', 'رهبری', 'مدیر پروژه'], keywords_en=['management', 'leadership', 'PM']),

    # Level 2: Product Management
    _c('mgmt-product', 'مدیر محصول', parent_slug='management', icon='management', color='#8b5cf6', sort_order=1,
       skills=['Product Strategy', 'Roadmapping', 'Agile', 'Scrum', 'User Stories',
               'A/B Testing', 'Data Analysis', 'Stakeholder Management'],
       positions=['مدیر محصول', 'Product Manager', 'Product Owner'],
       keywords_fa=['مدیر محصول', 'پروادکت منیجر'],
       keywords_en=['product manager', 'product owner', 'PM'],
       education=['کارشناسی ارشد MBA', 'مهندسی صنایع'],
       salary_range='۳۰ - ۱۰۰ میلیون تومان',
       career_path='PO → PM → Senior PM → Head of Product → VP Product'),

    # Level 2: Project Management
    _c('mgmt-project', 'مدیر پروژه', parent_slug='management', icon='management', color='#a78bfa', sort_order=2,
       skills=['Agile', 'Scrum', 'Kanban', 'Jira', 'Risk Management',
               'Budgeting', 'Resource Planning', 'Stakeholder Comm.'],
       positions=['مدیر پروژه', 'Project Manager', 'Scrum Master'],
       keywords_fa=['مدیر پروژه', 'اسکرام مستر', 'آجایل'],
       keywords_en=['project manager', 'scrum master', 'agile', 'PMP'],
       education=['MBA', 'PMP', 'مدرک Scrum'],
       salary_range='۲۵ - ۸۰ میلیون تومان'),

    # ── Level 1: Finance ──
    _c('finance', 'مالی و حسابداری', icon='finance', color='#10b981', sort_order=70,
       skills=['Excel', 'Accounting', 'Financial Analysis', 'Tax', 'Audit',
               'SAP', 'ERP', 'Budgeting', 'Reporting'],
       positions=['حسابدار', 'مدیر مالی', 'Financial Analyst', 'Accountant'],
       keywords_fa=['حسابداری', 'مالی', 'حسابرسی'],
       keywords_en=['accounting', 'finance', 'audit', 'financial analyst'],
       education=['کارشناسی حسابداری', 'MBA', 'CPA'],
       salary_range='۱۵ - ۵۰ میلیون تومان',
       jobvision_slug='accounting', irantalent_slug='accounting'),

    # ── Level 1: HR ──
    _c('hr', 'منابع انسانی', icon='hr', color='#f43f5e', sort_order=80,
       skills=['Recruiting', 'Onboarding', 'Payroll', 'Labor Law',
               'Performance Review', 'Training', 'HRIS', 'Organizational Design'],
       positions:['کارشناس منابع انسانی', 'HR Manager', 'Recruiter', 'Talent Acquisition'],
       keywords_fa=['منابع انسانی', 'نیروی انسانی', 'استخدام'],
       keywords_en=['HR', 'human resources', 'recruiting', 'talent acquisition'],
       education=['کارشناسی مدیریت منابع انسانی', 'ارشد MBA'],
       salary_range='۱۵ - ۵۰ میلیون تومان',
       jobvision_slug='hr', irantalent_slug='human-resources'),

    # ── Level 1: Content ──
    _c('content', 'تولید محتوا', icon='content', color='#f97316', sort_order=90,
       skills=['Copywriting', 'SEO Writing', 'Social Media', 'WordPress',
               'Video Editing', 'Photography', 'Canva', 'Content Strategy'],
       positions=['تولیدکننده محتوا', 'Content Writer', 'Copywriter', 'Content Manager'],
       keywords_fa=['تولید محتوا', 'نویسندگی', 'کپی‌رایتینگ'],
       keywords_en=['content writing', 'copywriting', 'content marketing'],
       education=['کارشناسی ارتباطات', 'مدرک مرتبط'],
       salary_range='۸ - ۳۰ میلیون تومان'),

    # ── Game Dev ──
    _c('eng-game', 'توسعه بازی', parent_slug='eng-computer', icon='game', color='#8b5cf6', sort_order=6,
       skills=['Unity', 'Unreal Engine', 'C#', 'C++', 'Blender', 'Game Design',
               'Physics Engine', '3D Modeling', 'Animation'],
       positions:['برنامه‌نویس بازی', 'Game Developer', 'Unity Developer'],
       keywords_fa=['بازی', 'گیم', 'یونیتی', 'آنریل'],
       keywords_en=['game development', 'unity', 'unreal engine'],
       education=['کارشناسی مهندسی کامپیوتر', 'گیم دیزاین'],
       salary_range='۱۵ - ۵۰ میلیون تومان'),
]


# ──────────────────────────────────────────────────
# TREE 2: Skills-Based (درخت مهارتی)
# Tech Area → Specialization → Tools → Jobs
# This tree is organized by SKILL CLUSTERS, not education.
# ──────────────────────────────────────────────────
SKILLS_TREE = [
    # Root: Programming Languages
    _c('sk-prog', 'زبان‌های برنامه‌نویسی', icon='developer', color='#6366f1', sort_order=100,
       keywords_fa=['برنامه‌نویسی', 'کدنویسی'], keywords_en=['programming', 'coding']),

    _c('sk-prog-python', 'پایتون', parent_slug='sk-prog', icon='developer', color='#22c55e', sort_order=1,
       skills=['Python', 'Django', 'Flask', 'FastAPI', 'Pandas', 'NumPy', 'Pytest'],
       positions=['Python Developer', 'Backend Developer', 'Data Scientist', 'ML Engineer'],
       keywords_en=['python', 'django', 'flask'],
       jobvision_slug='python', irantalent_slug='python'),

    _c('sk-prog-js', 'جاوا اسکریپت / تایپ‌اسکریپت', parent_slug='sk-prog', icon='frontend', color='#eab308', sort_order=2,
       skills=['JavaScript', 'TypeScript', 'Node.js', 'React', 'Vue.js', 'Next.js'],
       positions=['Frontend Developer', 'Full Stack Developer', 'Node Developer'],
       keywords_en=['javascript', 'typescript', 'node.js']),

    _c('sk-prog-java', 'جاوا', parent_slug='sk-prog', icon='developer', color='#ef4444', sort_order=3,
       skills=['Java', 'Spring Boot', 'Maven', 'Hibernate'],
       positions=['Java Developer', 'Backend Engineer'],
       keywords_en=['java', 'spring'],
       jobvision_slug='java', irantalent_slug='java'),

    _c('sk-prog-csharp', 'سی‌شارپ و دات‌نت', parent_slug='sk-prog', icon='developer', color='#7c3aed', sort_order=4,
       skills=['C#', '.NET', 'ASP.NET', 'Blazor', 'Entity Framework'],
       positions=['.NET Developer', 'C# Developer'],
       keywords_en=['c#', '.net'],
       jobvision_slug='csharp'),

    _c('sk-prog-php', 'پی‌اچ‌پی', parent_slug='sk-prog', icon='developer', color='#6366f1', sort_order=5,
       skills=['PHP', 'Laravel', 'WordPress', 'MySQL'],
       positions=['PHP Developer', 'Laravel Developer'],
       keywords_en=['php', 'laravel']),

    _c('sk-prog-mobile-lang', 'کاتلین و سوئیفت', parent_slug='sk-prog', icon='mobile', color='#ec4899', sort_order=6,
       skills=['Kotlin', 'Swift', 'Android SDK', 'iOS SDK'],
       positions=['Android Developer', 'iOS Developer'],
       keywords_en=['kotlin', 'swift', 'android', 'ios']),

    # Root: Cloud & DevOps
    _c('sk-cloud', 'ابر و داوآپس', icon='devops', color='#f97316', sort_order=110,
       skills=['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Terraform', 'CI/CD'],
       positions=['DevOps Engineer', 'Cloud Engineer', 'SRE'],
       keywords_fa=['داوآپس', 'ابر', 'کلاود'],
       keywords_en=['devops', 'cloud', 'aws', 'docker', 'kubernetes'],
       jobvision_slug='devops', irantalent_slug='devops'),

    # Root: AI & Data
    _c('sk-ai', 'هوش مصنوعی و یادگیری ماشین', icon='ai', color='#a855f7', sort_order=120,
       skills=['Machine Learning', 'Deep Learning', 'NLP', 'LLM', 'TensorFlow', 'PyTorch'],
       positions=['AI Engineer', 'ML Engineer', 'Data Scientist'],
       keywords_fa=['هوش مصنوعی', 'یادگیری ماشین'],
       keywords_en=['AI', 'ML', 'deep learning', 'NLP'],
       jobvision_slug='ai', irantalent_slug='data-science'),

    # Root: Databases
    _c('sk-db', 'دیتابیس و ذخیره‌سازی', icon='data', color='#14b8a6', sort_order=130,
       skills=['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'SQL Server'],
       positions=['DBA', 'Database Engineer', 'Backend Developer'],
       keywords_fa=['دیتابیس', 'پایگاه داده'],
       keywords_en=['database', 'SQL', 'postgresql', 'mongodb']),

    # Root: Security
    _c('sk-security', 'امنیت و شبکه', icon='security', color='#dc2626', sort_order=140,
       skills=['Penetration Testing', 'Network Security', 'Firewall', 'Cisco', 'Linux'],
       positions=['Security Engineer', 'Pentester', 'Network Engineer'],
       keywords_fa=['امنیت', 'شبکه', 'تست نفوذ'],
       keywords_en=['security', 'network', 'penetration testing']),
]


class Command(BaseCommand):
    help = 'Seed JobCategory tree (education-based + skills-based). Deletes old data first.'

    def handle(self, *args, **options):
        self.stdout.write('Deleting all existing categories...')
        JobCategory.objects.all().delete()

        all_cats = EDUCATION_TREE + SKILLS_TREE
        created = {}
        count = 0

        for cat_data in all_cats:
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

        # Stats
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
