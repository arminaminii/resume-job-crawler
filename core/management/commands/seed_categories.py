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
    'other': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>',
}

CATEGORIES = [
    {'name': 'برنامه‌نویسی و توسعه نرم‌افزار', 'slug': 'developer', 'icon': 'developer', 'color': '#6366f1', 'jv': 'developer', 'es': 'برنامه-نویسی', 'sort': 1,
     'skills': ['Python','JavaScript','TypeScript','Java','C#','C++','PHP','Ruby','Go','Rust','Swift','Kotlin','Dart','Django','Flask','FastAPI','Spring','Laravel','ASP.NET','Node.js','Git','Docker','Linux','SQL','REST API','GraphQL','Microservices','Agile','Scrum','OOP'],
     'positions': ['برنامه‌نویس','توسعه‌دهنده','Developer','Software Engineer','Backend Developer','Frontend Developer','Full Stack Developer','Tech Lead','Software Architect'],
     'kw_fa': ['برنامه‌نویسی','توسعه نرم‌افزار','نرم‌افزار','کدنویسی','وب‌سایت'], 'kw_en': ['programming','software development','coding','web development']},
    {'name': 'توسعه وب فرانت‌اند', 'slug': 'frontend', 'icon': 'frontend', 'color': '#8b5cf6', 'jv': 'developer', 'sort': 2,
     'skills': ['HTML','CSS','JavaScript','TypeScript','React','Vue.js','Angular','Next.js','Nuxt.js','Tailwind CSS','Bootstrap','SASS','Webpack','Vite','jQuery','Redux','Responsive Design','SEO'],
     'positions': ['Frontend Developer','Web Developer','UI Developer','React Developer','Vue Developer','Angular Developer'],
     'kw_fa': ['فرانت‌اند','وب','رابط کاربری','سایت'], 'kw_en': ['frontend','web','ui','html','css']},
    {'name': 'توسعه وب بک‌اند', 'slug': 'backend', 'icon': 'developer', 'color': '#3b82f6', 'jv': 'developer', 'sort': 3,
     'skills': ['Python','Django','Flask','FastAPI','Java','Spring Boot','Node.js','Express.js','C#','ASP.NET','PHP','Laravel','Go','SQL','PostgreSQL','MySQL','MongoDB','Redis','REST API','GraphQL','Docker','Kubernetes','Linux','Nginx','Celery'],
     'positions': ['Backend Developer','Server Developer','API Developer','Python Developer','Java Developer','Node.js Developer'],
     'kw_fa': ['بک‌اند','سرور','API','دیتابیس'], 'kw_en': ['backend','server','api','database']},
    {'name': 'توسعه موبایل', 'slug': 'mobile', 'icon': 'mobile', 'color': '#06b6d4', 'jv': 'mobile-developer', 'es': 'موبایل', 'sort': 4,
     'skills': ['Flutter','Dart','React Native','Swift','Kotlin','iOS','Android','Java','Firebase','SQLite','REST API'],
     'positions': ['Mobile Developer','Android Developer','iOS Developer','Flutter Developer','React Native Developer'],
     'kw_fa': ['موبایل','اندروید','iOS','اپلیکیشن'], 'kw_en': ['mobile','android','ios','app','flutter']},
    {'name': 'علم داده و تحلیل داده', 'slug': 'data-science', 'icon': 'data', 'color': '#10b981', 'jv': 'data-science', 'es': 'داده', 'sort': 5,
     'skills': ['Python','Pandas','NumPy','Scikit-learn','Matplotlib','Seaborn','SQL','PostgreSQL','Excel','Power BI','Tableau','R','SPSS','Apache Spark','Hadoop','ETL','Statistics','A/B Testing','Jupyter'],
     'positions': ['Data Analyst','Data Scientist','Business Analyst','BI Developer','Data Engineer'],
     'kw_fa': ['داده','تحلیل داده','علم داده','بیگ دیتا','آمار'], 'kw_en': ['data','analytics','data science','big data','statistics']},
    {'name': 'هوش مصنوعی و یادگیری ماشین', 'slug': 'ai-ml', 'icon': 'ai', 'color': '#f43f5e', 'jv': 'data-science', 'sort': 6,
     'skills': ['Python','TensorFlow','PyTorch','Scikit-learn','Keras','NLP','Computer Vision','Deep Learning','Machine Learning','OpenCV','Pandas','NumPy','Transformers','BERT','GPT','LangChain'],
     'positions': ['ML Engineer','AI Engineer','NLP Engineer','Computer Vision Engineer','Deep Learning Engineer','AI Researcher'],
     'kw_fa': ['هوش مصنوعی','یادگیری ماشین','یادگیری عمیق','NLP','بینایی ماشین'], 'kw_en': ['artificial intelligence','machine learning','deep learning','nlp','ai']},
    {'name': 'DevOps و زیرساخت', 'slug': 'devops', 'icon': 'devops', 'color': '#f59e0b', 'jv': 'devops', 'es': 'دواپس', 'sort': 7,
     'skills': ['Docker','Kubernetes','CI/CD','Jenkins','GitLab CI','GitHub Actions','AWS','Azure','GCP','Terraform','Ansible','Linux','Nginx','Prometheus','Grafana','ELK Stack'],
     'positions': ['DevOps Engineer','Site Reliability Engineer','Cloud Engineer','System Administrator','Infrastructure Engineer'],
     'kw_fa': ['دواپس','زیرساخت','سرور','ابر','CI/CD'], 'kw_en': ['devops','infrastructure','cloud','server','sre']},
    {'name': 'شبکه و سیستم‌ها', 'slug': 'network', 'icon': 'network', 'color': '#64748b', 'jv': 'it', 'sort': 8,
     'skills': ['Networking','TCP/IP','DNS','VPN','Firewall','Cisco','MikroTik','Windows Server','Linux Server','Active Directory','VMware','LAN','WAN'],
     'positions': ['Network Engineer','System Administrator','IT Manager','Help Desk'],
     'kw_fa': ['شبکه','سیستم','IT','پشتیبانی'], 'kw_en': ['network','system','it','support','admin']},
    {'name': 'امنیت سایبری', 'slug': 'security', 'icon': 'security', 'color': '#ef4444', 'jv': 'security', 'es': 'امنیت', 'sort': 9,
     'skills': ['Penetration Testing','Network Security','Web Security','OWASP','Burp Suite','Nmap','Wireshark','Metasploit','Firewall','SIEM','SOC','Python','Linux','Cryptography'],
     'positions': ['Security Engineer','Penetration Tester','Security Analyst','SOC Analyst','Bug Hunter'],
     'kw_fa': ['امنیت','سایبری','نفوذ','هکر','فایروال'], 'kw_en': ['security','cybersecurity','penetration','hacking','vulnerability']},
    {'name': 'طراحی گرافیک و UI/UX', 'slug': 'ui-ux', 'icon': 'design', 'color': '#ec4899', 'jv': 'ui-ux', 'es': 'طراحی', 'sort': 10,
     'skills': ['Figma','Adobe XD','Photoshop','Illustrator','After Effects','InDesign','UI Design','UX Design','User Research','Wireframing','Prototyping','Design System','Typography'],
     'positions': ['UI Designer','UX Designer','Graphic Designer','Product Designer','Visual Designer','Motion Designer','Art Director'],
     'kw_fa': ['طراحی','گرافیک','رابط کاربری','تجربه کاربری'], 'kw_en': ['design','graphic','ui','ux','figma','photoshop']},
    {'name': 'بازاریابی دیجیتال و سئو', 'slug': 'digital-marketing', 'icon': 'marketing', 'color': '#14b8a6', 'jv': 'digital-marketing', 'es': 'بازاریابی', 'sort': 11,
     'skills': ['SEO','Google Analytics','Google Ads','Facebook Ads','Content Marketing','Email Marketing','Social Media Marketing','Copywriting','WordPress','Shopify','Google Tag Manager','Marketing Automation','Growth Hacking'],
     'positions': ['Digital Marketer','SEO Specialist','Content Marketer','Social Media Manager','Growth Hacker','Marketing Manager'],
     'kw_fa': ['بازاریابی','سئو','SEO','محتوا','شبکه‌های اجتماعی','تبلیغات'], 'kw_en': ['marketing','seo','digital marketing','content','social media','advertising']},
    {'name': 'فروش و توسعه کسب‌وکار', 'slug': 'sales', 'icon': 'sales', 'color': '#f97316', 'jv': 'business-development', 'es': 'فروش', 'sort': 12,
     'skills': ['B2B Sales','Negotiation','CRM','Salesforce','Business Development','Lead Generation','Market Research','Excel','Presentation'],
     'positions': ['Sales Manager','Business Developer','Account Manager','Sales Representative','Customer Success Manager'],
     'kw_fa': ['فروش','بازاریابی','کسب‌وکار','نمایندگی'], 'kw_en': ['sales','business development','b2b','account','revenue']},
    {'name': 'مالی و حسابداری', 'slug': 'accounting', 'icon': 'finance', 'color': '#84cc16', 'jv': 'accounting', 'es': 'حسابداری', 'sort': 13,
     'skills': ['Excel','Accounting','Financial Analysis','Audit','SAP','ERP','Tax','Financial Reporting','Budgeting','Power BI','SQL'],
     'positions': ['Accountant','Financial Analyst','Auditor','Finance Manager','CFO','Tax Consultant'],
     'kw_fa': ['حسابداری','مالی','حسابرسی','بودجه','مالیات'], 'kw_en': ['accounting','finance','audit','tax','financial']},
    {'name': 'منابع انسانی', 'slug': 'hr', 'icon': 'hr', 'color': '#a855f7', 'jv': 'human-resources', 'es': 'منابع-انسانی', 'sort': 14,
     'skills': ['Recruitment','Talent Acquisition','Performance Management','Labor Law','HRIS','Payroll','Training','Interviewing'],
     'positions': ['HR Manager','Recruiter','Talent Acquisition Specialist','HR Specialist','Training Manager'],
     'kw_fa': ['منابع انسانی','استخدام','پرسنلی'], 'kw_en': ['hr','human resources','recruitment','talent','hiring']},
    {'name': 'مدیریت و رهبری', 'slug': 'management', 'icon': 'management', 'color': '#0ea5e9', 'jv': 'business-development', 'sort': 15,
     'skills': ['Project Management','Agile','Scrum','Kanban','Jira','Leadership','Strategic Planning','Team Management','Risk Management','PMP'],
     'positions': ['Project Manager','Product Manager','Scrum Master','Operations Manager','General Manager'],
     'kw_fa': ['مدیریت','رهبری','پروژه','مدیر','استراتژی'], 'kw_en': ['management','leadership','project','scrum','agile']},
    {'name': 'تولید محتوا و کپی‌رایتینگ', 'slug': 'content', 'icon': 'content', 'color': '#d946ef', 'jv': 'content', 'es': 'محتوا', 'sort': 16,
     'skills': ['Copywriting','Content Writing','SEO Writing','Storytelling','WordPress','Canva','Social Media Content','Translation'],
     'positions': ['Content Writer','Copywriter','Content Manager','Blogger','Technical Writer'],
     'kw_fa': ['محتوا','نویسندگی','کپی‌رایتینگ','وبلاگ'], 'kw_en': ['content','writing','copywriting','blog']},
    {'name': 'مهندسی صنایع', 'slug': 'industrial', 'icon': 'other', 'color': '#78716c', 'jv': 'engineering', 'sort': 17,
     'skills': ['Optimization','Supply Chain','Lean','Six Sigma','AutoCAD','MATLAB','Quality Control','ERP','SAP'],
     'positions': ['Industrial Engineer','Production Manager','Quality Engineer','Supply Chain Analyst'],
     'kw_fa': ['صنایع','تولید','کنترل کیفیت'], 'kw_en': ['industrial','production','quality','supply chain']},
    {'name': 'مهندسی برق و الکترونیک', 'slug': 'electrical', 'icon': 'other', 'color': '#eab308', 'jv': 'engineering', 'sort': 18,
     'skills': ['PLC','SCADA','AutoCAD','MATLAB','Circuit Design','Arduino','Raspberry Pi','Power Systems','Control Systems','Embedded Systems'],
     'positions': ['Electrical Engineer','Electronics Engineer','Control Engineer','Automation Engineer','Embedded Engineer'],
     'kw_fa': ['برق','الکترونیک','اتوماسیون','PLC'], 'kw_en': ['electrical','electronics','automation','plc','embedded']},
    {'name': 'پزشکی و سلامت', 'slug': 'medical', 'icon': 'other', 'color': '#22c55e', 'jv': 'healthcare', 'sort': 19,
     'skills': ['Medical Knowledge','Patient Care','Electronic Health Records','Pharmacology'],
     'positions': ['Doctor','Nurse','Pharmacist','Dentist','Medical Assistant','Lab Technician'],
     'kw_fa': ['پزشکی','بهداشت','درمان','دارو'], 'kw_en': ['medical','health','healthcare','pharmacy']},
    {'name': 'آموزش و تدریس', 'slug': 'education', 'icon': 'other', 'color': '#0d9488', 'jv': 'education', 'sort': 20,
     'skills': ['Teaching','Curriculum Development','E-Learning','PowerPoint','Educational Technology'],
     'positions': ['Teacher','Professor','Instructor','Trainer','Tutor'],
     'kw_fa': ['آموزش','تدریس','معلمی','مدرس'], 'kw_en': ['education','teaching','teacher','instructor']},
    {'name': 'سایر', 'slug': 'other', 'icon': 'other', 'color': '#94a3b8', 'sort': 99,
     'skills': [], 'positions': [], 'kw_fa': [], 'kw_en': []},
]


class Command(BaseCommand):
    help = 'Seed job categories'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for c in CATEGORIES:
            obj, is_new = JobCategory.objects.update_or_create(
                slug=c['slug'],
                defaults={
                    'name': c['name'],
                    'icon_svg': ICONS.get(c['icon'], ICONS['other']),
                    'color': c['color'],
                    'jobvision_slug': c.get('jv', ''),
                    'estekhdam_slug': c.get('es', ''),
                    'skills': c['skills'],
                    'positions': c['positions'],
                    'keywords_fa': c['kw_fa'],
                    'keywords_en': c['kw_en'],
                    'sort_order': c['sort'],
                }
            )
            if is_new:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'{created} created, {updated} updated'))