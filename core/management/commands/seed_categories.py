"""
Comprehensive job categories seed data for the Persian job market.
Covers all major categories from Jobvision, E-estekhdam, IranTalent.
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
    'legal': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7v10l10 5 10-5V7L12 2z"/><path d="M12 22V12"/><path d="M22 7L12 12 2 7"/></svg>',
    'engineering': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>',
    'logistics': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
    'construction': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20h20"/><path d="M5 20V8l7-5 7 5v12"/><path d="M9 20v-6h6v6"/></svg>',
    'customer-service': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>',
    'game': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"/><line x1="6" y1="10" x2="6.01" y2="10"/><line x1="10" y1="10" x2="10.01" y2="10"/><line x1="14" y1="14" x2="14.01" y2="14"/><line x1="18" y1="14" x2="18.01" y2="14"/></svg>',
    'science': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 3h6v7l5 7H4l5-7V3z"/><line x1="9" y1="3" x2="15" y2="3"/></svg>',
    'translation': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 8l6 6"/><path d="M4 14l6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="M22 22l-5-10-5 10"/><path d="M14 18h6"/></svg>',
    'agriculture': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22c4-4 8-7.5 8-12a8 8 0 10-16 0c0 4.5 4 8 8 12z"/><path d="M12 10a2 2 0 100-4 2 2 0 000 4z"/></svg>',
    'other': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>',
}

CATEGORIES = [
    # ===== Parent Categories (Tree Roots) =====
    {'name': 'فناوری اطلاعات و نرم‌افزار', 'slug': 'it-parent', 'icon': 'developer', 'color': '#6366f1', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['فناوری', 'نرم‌افزار', 'IT', 'کامپیوتر'], 'kw_en': ['IT', 'software', 'technology', 'computer']},
    {'name': 'طراحی و خلاقیت', 'slug': 'design-parent', 'icon': 'design', 'color': '#ec4899', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['طراحی', 'خلاقیت', 'هنر'], 'kw_en': ['design', 'creative', 'art']},
    {'name': 'بازاریابی و فروش', 'slug': 'marketing-parent', 'icon': 'marketing', 'color': '#14b8a6', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['بازاریابی', 'فروش', 'بازار'], 'kw_en': ['marketing', 'sales', 'business']},
    {'name': 'مالی و حسابداری', 'slug': 'finance-parent', 'icon': 'finance', 'color': '#84cc16', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['مالی', 'حسابداری', 'بانک'], 'kw_en': ['finance', 'accounting', 'banking']},
    {'name': 'منابع انسانی و مدیریت', 'slug': 'hr-mgmt-parent', 'icon': 'management', 'color': '#a855f7', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['منابع انسانی', 'مدیریت', 'اداری'], 'kw_en': ['HR', 'management', 'administration']},
    {'name': 'مهندسی', 'slug': 'engineering-parent', 'icon': 'engineering', 'color': '#ca8a04', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['مهندسی', 'تولید', 'صنععت'], 'kw_en': ['engineering', 'manufacturing', 'industry']},
    {'name': 'پزشکی و سلامت', 'slug': 'medical-parent', 'icon': 'medical', 'color': '#22c55e', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['پزشکی', 'بهداشت', 'درمان'], 'kw_en': ['medical', 'health', 'healthcare']},
    {'name': 'آموزش و پژوهش', 'slug': 'education-parent', 'icon': 'content', 'color': '#0d9488', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['آموزش', 'تدریس', 'پژوهش'], 'kw_en': ['education', 'teaching', 'research']},
    {'name': 'خدمات و سایر', 'slug': 'services-parent', 'icon': 'customer-service', 'color': '#64748b', 'sort': 0,
     'skills': [], 'positions': [], 'kw_fa': ['خدمات', 'اداری', 'پشتیبانی'], 'kw_en': ['services', 'support', 'operations']},

    # ===== فناوری اطلاعات و نرم‌افزار =====
    {'name': 'برنامه‌نویسی و توسعه نرم‌افزار', 'slug': 'developer', 'parent': 'it-parent', 'icon': 'developer', 'color': '#6366f1', 'jv': 'developer', 'es': 'برنامه-نویسی', 'sort': 1,
     'skills': ['Python','JavaScript','TypeScript','Java','C#','C++','PHP','Ruby','Go','Rust','Swift','Kotlin','Dart','Django','Flask','FastAPI','Spring','Laravel','ASP.NET','Node.js','Git','Docker','Linux','SQL','REST API','GraphQL','Microservices','Agile','Scrum','OOP'],
     'positions': ['برنامه‌نویس','توسعه‌دهنده','Developer','Software Engineer','Backend Developer','Frontend Developer','Full Stack Developer','Tech Lead','Software Architect'],
     'kw_fa': ['برنامه‌نویسی','توسعه نرم‌افزار','نرم‌افزار','کدنویسی','وب‌سایت'], 'kw_en': ['programming','software development','coding','web development']},
    {'name': 'توسعه وب فرانت‌اند', 'slug': 'frontend', 'parent': 'it-parent', 'icon': 'frontend', 'color': '#8b5cf6', 'jv': 'developer', 'sort': 2,
     'skills': ['HTML','CSS','JavaScript','TypeScript','React','Vue.js','Angular','Next.js','Nuxt.js','Tailwind CSS','Bootstrap','SASS','Webpack','Vite','jQuery','Redux','Responsive Design','SEO'],
     'positions': ['Frontend Developer','Web Developer','UI Developer','React Developer','Vue Developer','Angular Developer'],
     'kw_fa': ['فرانت‌اند','وب','رابط کاربری','سایت'], 'kw_en': ['frontend','web','ui','html','css']},
    {'name': 'توسعه وب بک‌اند', 'slug': 'backend', 'parent': 'it-parent', 'icon': 'developer', 'color': '#3b82f6', 'jv': 'developer', 'sort': 3,
     'skills': ['Python','Django','Flask','FastAPI','Java','Spring Boot','Node.js','Express.js','C#','ASP.NET','PHP','Laravel','Go','SQL','PostgreSQL','MySQL','MongoDB','Redis','REST API','GraphQL','Docker','Kubernetes','Linux','Nginx','Celery'],
     'positions': ['Backend Developer','Server Developer','API Developer','Python Developer','Java Developer','Node.js Developer'],
     'kw_fa': ['بک‌اند','سرور','API','دیتابیس'], 'kw_en': ['backend','server','api','database']},
    {'name': 'توسعه موبایل', 'slug': 'mobile', 'parent': 'it-parent', 'icon': 'mobile', 'color': '#06b6d4', 'jv': 'mobile-developer', 'es': 'موبایل', 'sort': 4,
     'skills': ['Flutter','Dart','React Native','Swift','Kotlin','iOS','Android','Java','Firebase','SQLite','REST API'],
     'positions': ['Mobile Developer','Android Developer','iOS Developer','Flutter Developer','React Native Developer'],
     'kw_fa': ['موبایل','اندروید','iOS','اپلیکیشن'], 'kw_en': ['mobile','android','ios','app','flutter']},
    {'name': 'علم داده و تحلیل داده', 'slug': 'data-science', 'parent': 'it-parent', 'icon': 'data', 'color': '#10b981', 'jv': 'data-science', 'es': 'داده', 'sort': 5,
     'skills': ['Python','Pandas','NumPy','Scikit-learn','Matplotlib','Seaborn','SQL','PostgreSQL','Excel','Power BI','Tableau','R','SPSS','Apache Spark','Hadoop','ETL','Statistics','A/B Testing','Jupyter'],
     'positions': ['Data Analyst','Data Scientist','Business Analyst','BI Developer','Data Engineer'],
     'kw_fa': ['داده','تحلیل داده','علم داده','بیگ دیتا','آمار'], 'kw_en': ['data','analytics','data science','big data','statistics']},
    {'name': 'هوش مصنوعی و یادگیری ماشین', 'slug': 'ai-ml', 'parent': 'it-parent', 'icon': 'ai', 'color': '#f43f5e', 'jv': 'data-science', 'sort': 6,
     'skills': ['Python','TensorFlow','PyTorch','Scikit-learn','Keras','NLP','Computer Vision','Deep Learning','Machine Learning','OpenCV','Pandas','NumPy','Transformers','BERT','GPT','LangChain'],
     'positions': ['ML Engineer','AI Engineer','NLP Engineer','Computer Vision Engineer','Deep Learning Engineer','AI Researcher'],
     'kw_fa': ['هوش مصنوعی','یادگیری ماشین','یادگیری عمیق','NLP','بینایی ماشین'], 'kw_en': ['artificial intelligence','machine learning','deep learning','nlp','ai']},
    {'name': 'DevOps و زیرساخت', 'slug': 'devops', 'parent': 'it-parent', 'icon': 'devops', 'color': '#f59e0b', 'jv': 'devops', 'es': 'دواپس', 'sort': 7,
     'skills': ['Docker','Kubernetes','CI/CD','Jenkins','GitLab CI','GitHub Actions','AWS','Azure','GCP','Terraform','Ansible','Linux','Nginx','Prometheus','Grafana','ELK Stack'],
     'positions': ['DevOps Engineer','Site Reliability Engineer','Cloud Engineer','System Administrator','Infrastructure Engineer'],
     'kw_fa': ['دواپس','زیرساخت','سرور','ابر','CI/CD'], 'kw_en': ['devops','infrastructure','cloud','server','sre']},
    {'name': 'شبکه و سیستم‌ها', 'slug': 'network', 'parent': 'it-parent', 'icon': 'network', 'color': '#64748b', 'jv': 'it', 'sort': 8,
     'skills': ['Networking','TCP/IP','DNS','VPN','Firewall','Cisco','MikroTik','Windows Server','Linux Server','Active Directory','VMware','LAN','WAN'],
     'positions': ['Network Engineer','System Administrator','IT Manager','Help Desk'],
     'kw_fa': ['شبکه','سیستم','IT','پشتیبانی'], 'kw_en': ['network','system','it','support','admin']},
    {'name': 'امنیت سایبری', 'slug': 'security', 'parent': 'it-parent', 'icon': 'security', 'color': '#ef4444', 'jv': 'security', 'es': 'امنیت', 'sort': 9,
     'skills': ['Penetration Testing','Network Security','Web Security','OWASP','Burp Suite','Nmap','Wireshark','Metasploit','Firewall','SIEM','SOC','Python','Linux','Cryptography'],
     'positions': ['Security Engineer','Penetration Tester','Security Analyst','SOC Analyst','Bug Hunter'],
     'kw_fa': ['امنیت','سایبری','نفوذ','هکر','فایروال'], 'kw_en': ['security','cybersecurity','penetration','hacking','vulnerability']},
    {'name': 'تست و کنترل کیفیت نرم‌افزار', 'slug': 'qa-testing', 'parent': 'it-parent', 'icon': 'developer', 'color': '#0891b2', 'jv': 'developer', 'es': 'تست-نرم-افزار', 'sort': 10,
     'skills': ['Selenium','Cypress','Playwright','Jest','PyTest','JUnit','Postman','JMeter','API Testing','Manual Testing','Test Planning','Bug Tracking','SQL'],
     'positions': ['QA Engineer','Test Engineer','SDET','Automation Engineer','Manual Tester','QA Lead'],
     'kw_fa': ['تست','کنترل کیفیت','QA','بگ','باگ'], 'kw_en': ['testing','qa','quality assurance','selenium','automation']},
    {'name': 'توسعه بازی و گیم', 'slug': 'game-dev', 'parent': 'it-parent', 'icon': 'game', 'color': '#7c3aed', 'jv': 'developer', 'sort': 11,
     'skills': ['Unity','Unreal Engine','C#','C++','Blender','3D Modeling','Game Design','Physics Engine','OpenGL','DirectX','Photon','Multiplayer'],
     'positions': ['Game Developer','Game Designer','3D Artist','Game Programmer','Unity Developer','Level Designer'],
     'kw_fa': ['بازی','گیم','گیمینگ','بازی‌سازی'], 'kw_en': ['game','gaming','unity','unreal','game development']},
    {'name': 'پایگاه داده و DBA', 'slug': 'database', 'parent': 'it-parent', 'icon': 'data', 'color': '#0d9488', 'jv': 'developer', 'sort': 12,
     'skills': ['SQL','PostgreSQL','MySQL','MongoDB','Redis','Oracle','SQL Server','Elasticsearch','Data Modeling','Replication','Backup','Performance Tuning','PL/SQL'],
     'positions': ['Database Administrator','DBA','Data Engineer','Database Developer','PostgreSQL DBA'],
     'kw_fa': ['دیتابیس','پایگاه داده','DBA','SQL'], 'kw_en': ['database','dba','sql','postgresql','mongodb']},

    # ===== طراحی و خلاقیت =====
    {'name': 'طراحی گرافیک و UI/UX', 'slug': 'ui-ux', 'parent': 'design-parent', 'icon': 'design', 'color': '#ec4899', 'jv': 'ui-ux', 'es': 'طراحی', 'sort': 13,
     'skills': ['Figma','Adobe XD','Photoshop','Illustrator','After Effects','InDesign','UI Design','UX Design','User Research','Wireframing','Prototyping','Design System','Typography'],
     'positions': ['UI Designer','UX Designer','Graphic Designer','Product Designer','Visual Designer','Motion Designer','Art Director'],
     'kw_fa': ['طراحی','گرافیک','رابط کاربری','تجربه کاربری'], 'kw_en': ['design','graphic','ui','ux','figma','photoshop']},
    {'name': 'طراحی وب و قالب', 'slug': 'web-design', 'parent': 'design-parent', 'icon': 'frontend', 'color': '#a855f7', 'jv': 'developer', 'es': 'طراحی-وب', 'sort': 14,
     'skills': ['HTML','CSS','JavaScript','Photoshop','Figma','Adobe XD','Responsive Design','WordPress','Webflow','UI Design'],
     'positions': ['Web Designer','UI Designer','Frontend Developer','WordPress Developer'],
     'kw_fa': ['طراحی وب','قالب','وردپرس','وب‌سایت'], 'kw_en': ['web design','wordpress','template','landing page']},
    {'name': 'انیمیشن و موشن‌گرافیک', 'slug': 'animation', 'parent': 'design-parent', 'icon': 'design', 'color': '#d946ef', 'jv': 'design', 'es': 'انیمیشن', 'sort': 15,
     'skills': ['After Effects','Premiere Pro','Cinema 4D','Blender','Maya','3D Animation','Motion Graphics','Character Animation','Storyboard'],
     'positions': ['Motion Designer','Animator','3D Artist','Video Editor','Animation Director'],
     'kw_fa': ['انیمیشن','موشن','ویدیو','تولید محتوای ویدیویی'], 'kw_en': ['animation','motion graphics','after effects','video']},
    {'name': 'عکاسی و تدوین ویدیو', 'slug': 'photography', 'parent': 'design-parent', 'icon': 'design', 'color': '#f472b6', 'jv': 'design', 'es': 'عکاسی', 'sort': 16,
     'skills': ['Photography','Photoshop','Lightroom','Premiere Pro','DaVinci Resolve','Final Cut Pro','After Effects','Color Grading','Lighting'],
     'positions': ['Photographer','Videographer','Video Editor','Colorist','Cameraman','Photo Editor'],
     'kw_fa': ['عکاسی','ویدیو','تدوین','فیلمبرداری'], 'kw_en': ['photography','video editing','videography','film']},

    # ===== بازاریابی و فروش =====
    {'name': 'بازاریابی دیجیتال و سئو', 'slug': 'digital-marketing', 'parent': 'marketing-parent', 'icon': 'marketing', 'color': '#14b8a6', 'jv': 'digital-marketing', 'es': 'بازاریابی', 'sort': 17,
     'skills': ['SEO','Google Analytics','Google Ads','Facebook Ads','Content Marketing','Email Marketing','Social Media Marketing','Copywriting','WordPress','Shopify','Google Tag Manager','Marketing Automation','Growth Hacking'],
     'positions': ['Digital Marketer','SEO Specialist','Content Marketer','Social Media Manager','Growth Hacker','Marketing Manager'],
     'kw_fa': ['بازاریابی','سئو','SEO','محتوا','شبکه‌های اجتماعی','تبلیغات'], 'kw_en': ['marketing','seo','digital marketing','content','social media','advertising']},
    {'name': 'فروش و توسعه کسب‌وکار', 'slug': 'sales', 'parent': 'marketing-parent', 'icon': 'sales', 'color': '#f97316', 'jv': 'business-development', 'es': 'فروش', 'sort': 18,
     'skills': ['B2B Sales','Negotiation','CRM','Salesforce','Business Development','Lead Generation','Market Research','Excel','Presentation'],
     'positions': ['Sales Manager','Business Developer','Account Manager','Sales Representative','Customer Success Manager'],
     'kw_fa': ['فروش','بازاریابی','کسب‌وکار','نمایندگی'], 'kw_en': ['sales','business development','b2b','account','revenue']},
    {'name': 'روابط عمومی و برندینگ', 'slug': 'pr-branding', 'parent': 'marketing-parent', 'icon': 'marketing', 'color': '#fb923c', 'jv': 'digital-marketing', 'es': 'روابط-عمومی', 'sort': 19,
     'skills': ['Public Relations','Brand Management','Media Relations','Event Planning','Crisis Communication','Social Media','Content Strategy','Copywriting'],
     'positions': ['PR Manager','Brand Manager','Communications Specialist','Event Manager','Media Relations Manager'],
     'kw_fa': ['روابط عمومی','برند','نام تجاری','ارتباطات'], 'kw_en': ['public relations','branding','communications','pr']},
    {'name': 'تولید محتوا و کپی‌رایتینگ', 'slug': 'content', 'parent': 'marketing-parent', 'icon': 'content', 'color': '#d946ef', 'jv': 'content', 'es': 'محتوا', 'sort': 20,
     'skills': ['Copywriting','Content Writing','SEO Writing','Storytelling','WordPress','Canva','Social Media Content','Translation'],
     'positions': ['Content Writer','Copywriter','Content Manager','Blogger','Technical Writer'],
     'kw_fa': ['محتوا','نویسندگی','کپی‌رایتینگ','وبلاگ'], 'kw_en': ['content','writing','copywriting','blog']},

    # ===== مالی و حسابداری =====
    {'name': 'مالی و حسابداری', 'slug': 'accounting', 'icon': 'finance', 'color': '#84cc16', 'jv': 'accounting', 'es': 'حسابداری', 'sort': 21,
     'skills': ['Excel','Accounting','Financial Analysis','Audit','SAP','ERP','Tax','Financial Reporting','Budgeting','Power BI','SQL'],
     'positions': ['Accountant','Financial Analyst','Auditor','Finance Manager','CFO','Tax Consultant'],
     'kw_fa': ['حسابداری','مالی','حسابرسی','بودجه','مالیات'], 'kw_en': ['accounting','finance','audit','tax','financial']},
    {'name': 'بازرگانی و امور مالی', 'slug': 'trade-finance', 'icon': 'finance', 'color': '#65a30d', 'jv': 'accounting', 'es': 'بازرگانی', 'sort': 22,
     'skills': ['Import/Export','Customs','Trade Finance','LC','Insurance','International Trade','Supply Chain','Contract Management'],
     'positions': ['Trade Specialist','Import/Export Manager','Commercial Manager','Customs Broker','Trade Finance Analyst'],
     'kw_fa': ['بازرگانی','صادرات','واردات','گمرک','تجارت'], 'kw_en': ['trade','import','export','commerce','business']},
    {'name': 'بیمه و بانکداری', 'slug': 'insurance-banking', 'icon': 'finance', 'color': '#16a34a', 'jv': 'accounting', 'es': 'بیمه', 'sort': 23,
     'skills': ['Insurance','Banking','Risk Management','Compliance','Financial Analysis','Credit Analysis','Loan Processing','Customer Service'],
     'positions': ['Insurance Agent','Banker','Risk Analyst','Loan Officer','Branch Manager','Compliance Officer'],
     'kw_fa': ['بیمه','بانک','مالی','ریسک','وام'], 'kw_en': ['insurance','banking','finance','risk','loan']},

    # ===== منابع انسانی و مدیریت =====
    {'name': 'منابع انسانی', 'slug': 'hr', 'icon': 'hr', 'color': '#a855f7', 'jv': 'human-resources', 'es': 'منابع-انسانی', 'sort': 24,
     'skills': ['Recruitment','Talent Acquisition','Performance Management','Labor Law','HRIS','Payroll','Training','Interviewing'],
     'positions': ['HR Manager','Recruiter','Talent Acquisition Specialist','HR Specialist','Training Manager'],
     'kw_fa': ['منابع انسانی','استخدام','پرسنلی'], 'kw_en': ['hr','human resources','recruitment','talent','hiring']},
    {'name': 'مدیریت و رهبری', 'slug': 'management', 'icon': 'management', 'color': '#0ea5e9', 'jv': 'business-development', 'es': 'مدیریت', 'sort': 25,
     'skills': ['Project Management','Agile','Scrum','Kanban','Jira','Leadership','Strategic Planning','Team Management','Risk Management','PMP'],
     'positions': ['Project Manager','Product Manager','Scrum Master','Operations Manager','General Manager'],
     'kw_fa': ['مدیریت','رهبری','پروژه','مدیر','استراتژی'], 'kw_en': ['management','leadership','project','scrum','agile']},
    {'name': 'خدمات مشتری و پشتیبانی', 'slug': 'customer-service', 'icon': 'customer-service', 'color': '#06b6d4', 'jv': 'customer-service', 'es': 'پشتیبانی', 'sort': 26,
     'skills': ['Customer Service','CRM','Communication','Problem Solving','Ticketing Systems','Zendesk','Live Chat','Phone Support','Salesforce'],
     'positions': ['Customer Service Representative','Support Agent','Call Center Agent','Customer Success Manager','Help Desk'],
     'kw_fa': ['پشتیبانی','خدمات مشتری','تماس','استقبال'], 'kw_en': ['customer service','support','help desk','call center']},

    # ===== مهندسی =====
    {'name': 'مهندسی صنایع', 'slug': 'industrial', 'icon': 'engineering', 'color': '#78716c', 'jv': 'engineering', 'es': 'صنایع', 'sort': 27,
     'skills': ['Optimization','Supply Chain','Lean','Six Sigma','AutoCAD','MATLAB','Quality Control','ERP','SAP'],
     'positions': ['Industrial Engineer','Production Manager','Quality Engineer','Supply Chain Analyst'],
     'kw_fa': ['صنایع','تولید','کنترل کیفیت'], 'kw_en': ['industrial','production','quality','supply chain']},
    {'name': 'مهندسی برق و الکترونیک', 'slug': 'electrical', 'icon': 'engineering', 'color': '#eab308', 'jv': 'engineering', 'es': 'برق', 'sort': 28,
     'skills': ['PLC','SCADA','AutoCAD','MATLAB','Circuit Design','Arduino','Raspberry Pi','Power Systems','Control Systems','Embedded Systems'],
     'positions': ['Electrical Engineer','Electronics Engineer','Control Engineer','Automation Engineer','Embedded Engineer'],
     'kw_fa': ['برق','الکترونیک','اتوماسیون','PLC'], 'kw_en': ['electrical','electronics','automation','plc','embedded']},
    {'name': 'مهندسی مکانیک', 'slug': 'mechanical', 'icon': 'engineering', 'color': '#a16207', 'jv': 'engineering', 'es': 'مکانیک', 'sort': 29,
     'skills': ['AutoCAD','SolidWorks','CATIA','ANSYS','MATLAB','Thermodynamics','Fluid Mechanics','Manufacturing','CNC','3D Modeling'],
     'positions': ['Mechanical Engineer','Design Engineer','Manufacturing Engineer','Maintenance Engineer','CAD Designer'],
     'kw_fa': ['مکانیک','طراحی صنعتی','تولید','CNC'], 'kw_en': ['mechanical','design','manufacturing','cad','engineering']},
    {'name': 'مهندسی عمران و معماری', 'slug': 'civil-architecture', 'icon': 'construction', 'color': '#ca8a04', 'jv': 'engineering', 'es': 'عمران', 'sort': 30,
     'skills': ['AutoCAD','Revit','SketchUp','3ds Max','ETABS','STAAD','Project Management','Construction','Structural Design','BIM'],
     'positions': ['Civil Engineer','Architect','Structural Engineer','Site Engineer','Project Manager','BIM Specialist'],
     'kw_fa': ['عمران','معماری','ساختمان','پروژه ساختمانی'], 'kw_en': ['civil','architecture','construction','structural','bim']},
    {'name': 'مهندسی شیمی و نفت', 'slug': 'chemical-petroleum', 'icon': 'science', 'color': '#dc2626', 'jv': 'engineering', 'es': 'شیمی', 'sort': 31,
     'skills': ['Chemical Engineering','Process Design','HYSYS','MATLAB','Lab Equipment','Quality Control','Safety','Environmental'],
     'positions': ['Chemical Engineer','Process Engineer','Petroleum Engineer','Lab Technician','HSE Engineer'],
     'kw_fa': ['شیمی','نفت','پتروشیمی','پالایشگاه'], 'kw_en': ['chemical','petroleum','process','engineering','oil']},
    {'name': 'مهندسی کامپیوتر و سخت‌افزار', 'slug': 'hardware', 'icon': 'engineering', 'color': '#2563eb', 'jv': 'it', 'es': 'سخت-افزار', 'sort': 32,
     'skills': ['VHDL','Verilog','FPGA','PCB Design','Altium','C','Assembly','Embedded C','Microcontroller','ARM','IoT','Raspberry Pi','Arduino'],
     'positions': ['Hardware Engineer','Embedded Engineer','FPGA Engineer','PCB Designer','IoT Engineer','Firmware Developer'],
     'kw_fa': ['سخت‌افزار','تعبیه‌شده','IoT','مدار'], 'kw_en': ['hardware','embedded','fpga','pcb','iot','firmware']},

    # ===== پزشکی و سلامت =====
    {'name': 'پزشکی و سلامت', 'slug': 'medical', 'icon': 'medical', 'color': '#22c55e', 'jv': 'healthcare', 'es': 'پزشکی', 'sort': 33,
     'skills': ['Medical Knowledge','Patient Care','Electronic Health Records','Pharmacology','Diagnosis','Treatment Planning','Clinical Research'],
     'positions': ['Doctor','General Practitioner','Specialist','Medical Assistant','Lab Technician','Researcher'],
     'kw_fa': ['پزشکی','بهداشت','درمان','دارو'], 'kw_en': ['medical','health','healthcare','pharmacy','clinical']},
    {'name': 'پرستاری و مامایی', 'slug': 'nursing', 'icon': 'medical', 'color': '#16a34a', 'jv': 'healthcare', 'es': 'پرستاری', 'sort': 34,
     'skills': ['Patient Care','Nursing','First Aid','Medical Records','Vital Signs','Medication Administration','Communication'],
     'positions': ['Nurse','Head Nurse','ICU Nurse','Midwife','Nursing Assistant'],
     'kw_fa': ['پرستاری','مامایی','بیمارستان','مراقبت'], 'kw_en': ['nursing','healthcare','patient care','medical']},
    {'name': 'داروسازی و علوم آزمایشگاهی', 'slug': 'pharmacy-lab', 'icon': 'science', 'color': '#059669', 'jv': 'healthcare', 'es': 'داروسازی', 'sort': 35,
     'skills': ['Pharmacology','Pharmaceutical','Lab Equipment','Quality Control','Clinical Trials','Regulatory Affairs','GMP'],
     'positions': ['Pharmacist','Lab Technician','Quality Control Analyst','Clinical Research Associate','Regulatory Affairs Specialist'],
     'kw_fa': ['داروسازی','آزمایشگاه','دارو','تحقیقات بالینی'], 'kw_en': ['pharmacy','laboratory','pharmaceutical','clinical research']},

    # ===== آموزش و پژوهش =====
    {'name': 'آموزش و تدریس', 'slug': 'education', 'icon': 'content', 'color': '#0d9488', 'jv': 'education', 'es': 'آموزش', 'sort': 36,
     'skills': ['Teaching','Curriculum Development','E-Learning','PowerPoint','Educational Technology','Classroom Management','Lesson Planning'],
     'positions': ['Teacher','Professor','Instructor','Trainer','Tutor','Education Consultant'],
     'kw_fa': ['آموزش','تدریس','معلمی','مدرس'], 'kw_en': ['education','teaching','teacher','instructor']},
    {'name': 'تحقیق و پژوهش', 'slug': 'research', 'icon': 'science', 'color': '#7c3aed', 'jv': 'education', 'es': 'پژوهش', 'sort': 37,
     'skills': ['Research','Data Analysis','Academic Writing','SPSS','MATLAB','Statistics','Publication','Literature Review','Grant Writing'],
     'positions': ['Researcher','Research Assistant','Professor','Scientist','Analyst'],
     'kw_fa': ['پژوهش','تحقیق','دانشگاه','علمی'], 'kw_en': ['research','academic','science','analysis','university']},

    # ===== حقوق و قضایی =====
    {'name': 'حقوق و قضایی', 'slug': 'legal', 'icon': 'legal', 'color': '#b45309', 'jv': 'legal', 'es': 'حقوق', 'sort': 38,
     'skills': ['Law','Legal Research','Contract Law','Labor Law','Commercial Law','Legal Writing','Negotiation','Litigation','Arbitration'],
     'positions': ['Lawyer','Legal Consultant','Legal Assistant','Judge','Notary','Compliance Officer'],
     'kw_fa': ['حقوق','وکیل','قضایی','قرارداد','دعاوی'], 'kw_en': ['law','legal','lawyer','attorney','compliance']},

    # ===== لجستیک و حمل‌ونقل =====
    {'name': 'لجستیک و حمل‌ونقل', 'slug': 'logistics', 'icon': 'logistics', 'color': '#0284c7', 'jv': 'logistics', 'es': 'لجستیک', 'sort': 39,
     'skills': ['Supply Chain','Warehouse Management','Inventory','Shipping','Import/Export','ERP','SAP','Logistics','Fleet Management'],
     'positions': ['Logistics Manager','Warehouse Manager','Supply Chain Manager','Fleet Manager','Import/Export Specialist'],
     'kw_fa': ['لجستیک','انبار','حمل‌ونقل','توزیع'], 'kw_en': ['logistics','supply chain','warehouse','transportation','shipping']},

    # ===== کشاورزی و دامپروری =====
    {'name': 'کشاورزی و دامپروری', 'slug': 'agriculture', 'icon': 'agriculture', 'color': '#15803d', 'jv': 'agriculture', 'es': 'کشاورزی', 'sort': 40,
     'skills': ['Agriculture','Irrigation','Pest Control','Crop Management','Livestock','Farm Management','Organic Farming','Agricultural Machinery'],
     'positions': ['Agricultural Engineer','Farm Manager','Agronomist','Veterinarian','Irrigation Specialist'],
     'kw_fa': ['کشاورزی','دامپروری','دامی','زراعت'], 'kw_en': ['agriculture','farming','livestock','irrigation','agronomy']},

    # ===== ترجمه و زبان =====
    {'name': 'ترجمه و زبان‌های خارجی', 'slug': 'translation', 'icon': 'translation', 'color': '#6d28d9', 'jv': 'content', 'es': 'ترجمه', 'sort': 41,
     'skills': ['English','Translation','Interpretation','Proofreading','Localization','Subtitling','CAT Tools','Grammar','Writing'],
     'positions': ['Translator','Interpreter','Proofreader','Localization Specialist','English Teacher','Subtitler'],
     'kw_fa': ['ترجمه','زبان','انگلیسی','مترجم'], 'kw_en': ['translation','english','language','interpreter','localization']},

    # ===== اداری و دفتری =====
    {'name': 'اداری و دفتری', 'slug': 'administrative', 'icon': 'content', 'color': '#64748b', 'jv': 'administrative', 'es': 'اداری', 'sort': 42,
     'skills': ['Microsoft Office','Excel','Word','PowerPoint','Data Entry','Filing','Scheduling','Communication','Organization'],
     'positions': ['Secretary','Office Manager','Administrative Assistant','Receptionist','Data Entry Operator','Clerk'],
     'kw_fa': ['اداری','دفتری','منشی','بایگانی'], 'kw_en': ['administrative','office','secretary','clerk','data entry']},
    {'name': 'گردشگری و هتلداری', 'slug': 'tourism-hospitality', 'icon': 'customer-service', 'color': '#0891b2', 'jv': 'customer-service', 'es': 'گردشگری', 'sort': 43,
     'skills': ['Hospitality','Customer Service','Tour Planning','Hotel Management','Booking Systems','Languages','Event Planning','Food Service'],
     'positions': ['Tour Guide','Hotel Manager','Travel Agent','Receptionist','Event Coordinator','Chef'],
     'kw_fa': ['گردشگری','هتل','تور','مسافرت'], 'kw_en': ['tourism','hospitality','hotel','travel','guide']},

    # ===== رسانه و هنر =====
    {'name': 'روزنامه‌نگاری و رسانه', 'slug': 'journalism', 'icon': 'content', 'color': '#be123c', 'jv': 'content', 'es': 'رسانه', 'sort': 44,
     'skills': ['Journalism','News Writing','Editing','Investigative Reporting','Social Media','SEO','Photography','Video','Interviewing'],
     'positions': ['Journalist','Editor','Reporter','News Anchor','Editor-in-Chief','Content Manager'],
     'kw_fa': ['روزنامه‌نگاری','رسانه','خبر','تحریریه'], 'kw_en': ['journalism','media','news','reporting','editing']},

    # ===== خدمات فنی و ساختمان =====
    {'name': 'خدمات فنی و ساختمان', 'slug': 'trades', 'icon': 'construction', 'color': '#92400e', 'jv': 'engineering', 'es': 'ساختمان', 'sort': 45,
     'skills': ['Welding','Plumbing','Electrical Wiring','Painting','Masonry','Carpentry','HVAC','Building Maintenance','Safety'],
     'positions': ['Technician','Electrician','Plumber','Welder','Carpenter','HVAC Technician','Building Manager'],
     'kw_fa': ['فنی','ساختمان','تاسیسات','لوله‌کشی','برق‌کاری'], 'kw_en': ['trades','construction','maintenance','technician','plumbing']},

    # ===== علمی و آزمایشگاهی =====
    {'name': 'علوم آزمایشگاهی و محیط زیست', 'slug': 'lab-environment', 'icon': 'science', 'color': '#047857', 'jv': 'healthcare', 'es': 'آزمایشگاه', 'sort': 46,
     'skills': ['Laboratory','HSE','Environmental Science','Chemistry','Biology','Quality Control','ISO','Safety Standards','Waste Management'],
     'positions': ['Lab Technician','HSE Officer','Environmental Engineer','Quality Inspector','Safety Officer'],
     'kw_fa': ['آزمایشگاه','محیط زیست','HSE','ایمنی'], 'kw_en': ['laboratory','environment','hse','safety','quality']},

    # ===== سایر =====
    {'name': 'سایر', 'slug': 'other', 'icon': 'other', 'color': '#94a3b8', 'sort': 99,
     'skills': [], 'positions': [], 'kw_fa': [], 'kw_en': []},
]

# Job tree enrichment data: education, certifications, salary range, career path
TREE_DATA = {
    'developer': {'edu': ['کارشناسی', 'Bachelor', 'Master'], 'certs': [], 'salary': '۱۵ تا ۷۰ میلیون تومان', 'path': 'جونیور > میان‌رده > ارشد > Tech Lead > CTO'},
    'frontend': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۱۲ تا ۵۰ میلیون تومان', 'path': 'جونیور فرانت > ارشد فرانت > Lead Frontend > Frontend Architect'},
    'backend': {'edu': ['کارشناسی', 'Bachelor', 'Master'], 'certs': [], 'salary': '۱۵ تا ۶۰ میلیون تومان', 'path': 'جونیور بک‌اند > ارشد بک‌اند > Tech Lead > Software Architect'},
    'mobile': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۱۵ تا ۵۵ میلیون تومان', 'path': 'جونیور موبایل > ارشد موبایل > Mobile Lead > Mobile Architect'},
    'data-science': {'edu': ['کارشناسی ارشد', 'Master', 'PhD'], 'certs': ['Google Data Analytics'], 'salary': '۲۰ تا ۸۰ میلیون تومان', 'path': 'تحلیلگر داده > دانشمند داده > Senior Data Scientist > Head of Data'},
    'ai-ml': {'edu': ['کارشناسی ارشد', 'Master', 'PhD'], 'certs': ['TensorFlow Certificate', 'AWS ML'], 'salary': '۲۵ تا ۱۰۰ میلیون تومان', 'path': 'ML Engineer > Senior ML > AI Lead > AI Director'},
    'devops': {'edu': ['کارشناسی', 'Bachelor'], 'certs': ['AWS Solutions Architect', 'Docker Certified', 'Kubernetes CKA'], 'salary': '۲۰ تا ۷۰ میلیون تومان', 'path': 'DevOps Junior > DevOps Engineer > SRE > Platform Engineer > DevOps Lead'},
    'network': {'edu': ['کارشناسی', 'Bachelor', 'Network+'], 'certs': ['CCNA', 'CCNP', 'MikroTik MTCNA'], 'salary': '۱۰ تا ۴۵ میلیون تومان', 'path': 'تکنسین شبکه > مهندس شبکه > مدیر شبکه > IT Manager'},
    'security': {'edu': ['کارشناسی ارشد', 'Master'], 'certs': ['CEH', 'OSCP', 'CompTIA Security+'], 'salary': '۲۵ تا ۹۰ میلیون تومان', 'path': 'تحلیلگر امنیت > مهندس امنیت > Security Lead > CISO'},
    'qa-testing': {'edu': ['کارشناسی', 'Bachelor'], 'certs': ['ISTQB'], 'salary': '۱۰ تا ۴۰ میلیون تومان', 'path': 'تستر دستی > تستر اتومیشن > QA Lead > SDET Lead > Head of QA'},
    'game-dev': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۱۵ تا ۵۰ میلیون تومان', 'path': 'جونیور بازی > گیم دولوپر > سینیر گیمر > Lead Game Developer > Technical Director'},
    'database': {'edu': ['کارشناسی', 'Bachelor'], 'certs': ['Oracle OCP', 'PostgreSQL Certified'], 'salary': '۱۵ تا ۵۰ میلیون تومان', 'path': 'DBA Junior > DBA > Senior DBA > Database Architect > Data Platform Lead'},
    'ui-ux': {'edu': ['کارشناسی', 'Bachelor'], 'certs': ['Google UX Design'], 'salary': '۱۰ تا ۴۵ میلیون تومان', 'path': 'طراحح مبتدی > UI Designer > UX Designer > Product Designer > Design Director'},
    'web-design': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۸ تا ۳۵ میلیون تومان', 'path': 'طراح وب مبتدی > طراح وب > ارشد طراح وب > Art Director'},
    'animation': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۱۰ تا ۴۰ میلیون تومان', 'path': 'انیماتور مبتدی > انیماتور > ارشد > Animation Director'},
    'photography': {'edu': ['دیپلم', 'Associate'], 'certs': [], 'salary': '۸ تا ۳۰ میلیون تومان', 'path': 'عکاس مبتدی > عکاس حرفه‌ای > سرپرست تیم > استودیو'},
    'digital-marketing': {'edu': ['کارشناسی', 'Bachelor'], 'certs': ['Google Ads', 'Google Analytics', 'HubSpot'], 'salary': '۱۰ تا ۵۰ میلیون تومان', 'path': 'بازاریاب مبتدی > متخصص دیجیتال > مدیر بازاریابی > CMO'},
    'sales': {'edu': ['کارشناسی', 'Bachelor', 'MBA'], 'certs': [], 'salary': '۱۰ تا ۶۰ میلیون تومان', 'path': 'فروشنده > نماینده > مدیر فروش > Sales Director > VP Sales'},
    'pr-branding': {'edu': ['کارشناسی', 'Bachelor', 'MBA'], 'certs': [], 'salary': '۱۲ تا ۴۵ میلیون تومان', 'path': 'کارشناس PR > مدیر PR > Brand Manager > Communications Director'},
    'content': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۸ تا ۳۵ میلیون تومان', 'path': 'نویسنده مبتدی > کپی‌رایتر > Content Manager > Head of Content'},
    'accounting': {'edu': ['کارشناسی', 'Bachelor'], 'certs': ['CMA', 'ACCA', 'CIA'], 'salary': '۱۰ تا ۴۵ میلیون تومان', 'path': 'حسابدار > حسابدار ارشد > مدیر مالی > CFO'},
    'trade-finance': {'edu': ['کارشناسی', 'Bachelor', 'MBA'], 'certs': ['CFA'], 'salary': '۱۵ تا ۶۰ میلیون تومان', 'path': 'تحلیلگر مالی > مدیر مالی > CFO'},
    'finance': {'edu': ['کارشناسی ارشد', 'Master', 'MBA'], 'certs': ['CFA', 'FRM'], 'salary': '۲۰ تا ۸۰ میلیون تومان', 'path': 'تحلیلگر > مدیر سرمایه‌گذاری > مدیر عامل مالی'},
    'hr': {'edu': ['کارشناسی', 'Bachelor', 'MBA'], 'certs': ['SHRM', 'PHR'], 'salary': '۱۲ تا ۵۰ میلیون تومان', 'path': 'کارشناس HR > مدیر HR > HR Business Partner > CHRO'},
    'management': {'edu': ['کارشناسی ارشد', 'Master', 'MBA'], 'certs': ['PMP'], 'salary': '۲۵ تا ۱۰۰ میلیون تومان', 'path': 'مدیر عملیات > مدیر ارشد > مدیرعامل > CEO'},
    'project-mgmt': {'edu': ['کارشناسی', 'Bachelor', 'MBA'], 'certs': ['PMP', 'PRINCE2', 'Scrum Master'], 'salary': '۱۵ تا ۶۰ میلیون تومان', 'path': 'هماهنگ‌کننده > مدیر پروژه > Senior PM > PMO Director'},
    'civil-eng': {'edu': ['کارشناسی', 'Bachelor', 'Master'], 'certs': [], 'salary': '۱۲ تا ۵۰ میلیون تومان', 'path': 'مهندس مبتدی > مهندس ارشد > مدیر پروژه > مدیر فنی'},
    'industrial-eng': {'edu': ['کارشناسی', 'Master'], 'certs': [], 'salary': '۱۵ تا ۵۰ میلیون تومان', 'path': 'مهندس صنایع > ارشد > مدیر تولید > مدیر کارخانه'},
    'mechanical-eng': {'edu': ['کارشناسی', 'Master'], 'certs': [], 'salary': '۱۲ تا ۵۰ میلیون تومان', 'path': 'مهندس مکانیک > ارشد > مدیر مهندسی > مدیر فنی'},
    'electrical-eng': {'edu': ['کارشناسی', 'Master'], 'certs': [], 'salary': '۱۲ تا ۵۰ میلیون تومان', 'path': 'مهندس برق > ارشد > مدیر پروژه برق > مدیر فنی'},
    'medical': {'edu': ['دکترای عمومی', 'MD', 'GP'], 'certs': ['بورد تخصصی'], 'salary': '۲۵ تا ۱۵۰ میلیون تومان', 'path': 'پزشک عمومی > متخصص > فوق تخصص > استاد دانشگاه'},
    'nursing': {'edu': ['کارشناسی پرستاری', 'BSc Nursing'], 'certs': [], 'salary': '۱۰ تا ۳۵ میلیون تومان', 'path': 'پرستار > سرپرستار > مدیر پرستاری > مدیر آموزش پرستاری'},
    'pharmacy-lab': {'edu': ['دکترای داروسازی', 'PharmD'], 'certs': [], 'salary': '۱۵ تا ۵۰ میلیون تومان', 'path': 'داروساز > مسئول فنی > مدیر آزمایشگاه > مدیر داروخانه'},
    'education': {'edu': ['کارشناسی ارشد', 'Master', 'PhD'], 'certs': [], 'salary': '۸ تا ۳۰ میلیون تومان', 'path': 'معلم > استاد > استادیار > دانشیار > استاد تمام'},
    'research': {'edu': ['کارشناسی ارشد', 'Master', 'PhD'], 'certs': [], 'salary': '۱۵ تا ۴۰ میلیون تومان', 'path': 'محقق > پژوهشگر ارشد > استادیار > استاد'},
    'legal': {'edu': ['کارشناسی ارشد', 'Master', 'PhD Law'], 'certs': ['گذرنامه وکالت'], 'salary': '۱۵ تا ۶۰ میلیون تومان', 'path': 'کارآموز وکالت > وکیل > وکیل ارشد > شریک دفتر > قاضی'},
    'logistics': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۱۰ تا ۴۰ میلیون تومان', 'path': 'کارشناس لجستیک > مدیر انبار > مدیر لجستیک > مدیر کل زنجیره تامین'},
    'agriculture': {'edu': ['کارشناسی', 'Bachelor', 'Master'], 'certs': [], 'salary': '۱۰ تا ۳۵ میلیون تومان', 'path': 'مهندس کشاورزی > کارشناس ارشد > مدیر مزرعه > مشاور'},
    'translation': {'edu': ['کارشناسی', 'Bachelor', 'Master'], 'certs': [], 'salary': '۸ تا ۳۰ میلیون تومان', 'path': 'مترجم مبتدی > مترجم حرفه‌ای > مترجم ارشد > مدیر تیم ترجمه'},
    'administrative': {'edu': ['دیپلم', 'Associate', 'Bachelor'], 'certs': ['ICDL'], 'salary': '۸ تا ۲۵ میلیون تومان', 'path': 'کارشناس اداری > منشی > مدیر دفتر > مدیر اداری'},
    'tourism-hospitality': {'edu': ['کارشناسی', 'Bachelor'], 'certs': [], 'salary': '۸ تا ۳۰ میلیون تومان', 'path': 'کارشناس هتل > مدیر رزرویشن > مدیر هتل > مدیر گردشگری'},
    'journalism': {'edu': ['کارشناسی', 'Bachelor', 'Master'], 'certs': [], 'salary': '۱۰ تا ۳۵ میلیون تومان', 'path': 'خبرنگار مبتدی > گزارشگر > سردبیر > سردبیر ارشد > مدیر تحریریه'},
    'trades': {'edu': ['دیپلم فنی', 'فوق دیپلم'], 'certs': [], 'salary': '۸ تا ۲۵ میلیون تومان', 'path': 'شاگرد > تکنسین > استادکار > سرپرست کارگاه'},
    'lab-environment': {'edu': ['کارشناسی', 'Bachelor', 'Master'], 'certs': ['HSE', 'ISO 14001'], 'salary': '۱۰ تا ۳۵ میلیون تومان', 'path': 'تکنسین آزمایشگاه > کارشناس HSE > مدیر HSE > مدیر محیط زیست'},
}


class Command(BaseCommand):
    help = 'Seed job categories with full tree data'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for c in CATEGORIES:
            parent_obj = None
            parent_slug = c.get('parent', '')
            if parent_slug:
                parent_obj = JobCategory.objects.filter(slug=parent_slug).first()

            # Get tree enrichment data
            td = TREE_DATA.get(c['slug'], {})

            obj, is_new = JobCategory.objects.update_or_create(
                slug=c['slug'],
                defaults={
                    'name': c['name'],
                    'parent': parent_obj,
                    'icon_svg': ICONS.get(c['icon'], ICONS['other']),
                    'color': c['color'],
                    'jobvision_slug': c.get('jv', ''),
                    'estekhdam_slug': c.get('es', ''),
                    'irantalent_slug': c.get('it', ''),
                    'skills': c['skills'],
                    'positions': c['positions'],
                    'keywords_fa': c['kw_fa'],
                    'keywords_en': c['kw_en'],
                    'education': c.get('edu', td.get('edu', [])),
                    'certifications': c.get('certs', td.get('certs', [])),
                    'salary_range': c.get('salary', td.get('salary', '')),
                    'career_path': c.get('path', td.get('path', '')),
                    'sort_order': c['sort'],
                }
            )
            if is_new:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'{created} created, {updated} updated. '
            f'Tree data: {len(TREE_DATA)} categories enriched.'
        ))