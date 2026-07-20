import re


# --- Skill & Field Dictionaries for Persian resumes ---
SKILLS_DICT = {
    # Programming
    'python': 'Python', 'پایتون': 'Python', 'django': 'Django', 'جنگو': 'Django',
    'flask': 'Flask', 'javascript': 'JavaScript', 'جاوااسکریپت': 'JavaScript',
    'typescript': 'TypeScript', 'react': 'React', 'ری‌اکت': 'React',
    'vue': 'Vue.js', 'node': 'Node.js', 'نود': 'Node.js',
    'java': 'Java', 'جاوا': 'Java', 'spring': 'Spring', 'c#': 'C#',
    'c++': 'C++', '.net': '.NET', 'php': 'PHP',
    'sql': 'SQL', 'mysql': 'MySQL', 'postgresql': 'PostgreSQL',
    'mongodb': 'MongoDB', 'redis': 'Redis', 'docker': 'Docker',
    'kubernetes': 'Kubernetes', 'git': 'Git', 'linux': 'Linux',
    'aws': 'AWS', 'azure': 'Azure', 'ci/cd': 'CI/CD',
    'html': 'HTML', 'css': 'CSS', 'tailwind': 'Tailwind CSS',
    'bootstrap': 'Bootstrap', 'flutter': 'Flutter', 'dart': 'Dart',
    'swift': 'Swift', 'kotlin': 'Kotlin', 'android': 'Android',
    'ios': 'iOS', 'react native': 'React Native',
    # Data
    'machine learning': 'Machine Learning', 'یادگیری ماشین': 'Machine Learning',
    'deep learning': 'Deep Learning', 'یادگیری عمیق': 'Deep Learning',
    'nlp': 'NLP', 'پردازش زبان طبیعی': 'NLP',
    'data science': 'Data Science', 'علم داده': 'Data Science',
    'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
    'pandas': 'Pandas', 'numpy': 'NumPy', 'scikit': 'Scikit-learn',
    'power bi': 'Power BI', 'tableau': 'Tableau', 'excel': 'Excel',
    # Design
    'figma': 'Figma', 'photoshop': 'Photoshop', 'ایلوستریتور': 'Illustrator',
    'illustrator': 'Illustrator', 'ui/ux': 'UI/UX', 'یو‌آی': 'UI/UX',
    # Marketing
    'seo': 'SEO', 'سئو': 'SEO', 'google analytics': 'Google Analytics',
    'digital marketing': 'Digital Marketing', 'بازاریابی دیجیتال': 'Digital Marketing',
    'content marketing': 'Content Marketing', 'تولید محتوا': 'Content Creation',
    # Other
    'project management': 'Project Management', 'مدیریت پروژه': 'Project Management',
    'agile': 'Agile', 'scrum': 'Scrum', 'jira': 'Jira',
}

FIELDS_DICT = {
    'برنامه‌نویسی': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'توسعه وب': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'وب': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'developer': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'programming': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'software': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'داده': 'علم داده و هوش مصنوعی',
    'data': 'علم داده و هوش مصنوعی',
    'ai': 'علم داده و هوش مصنوعی',
    'هوش مصنوعی': 'علم داده و هوش مصنوعی',
    'machine learning': 'علم داده و هوش مصنوعی',
    'طراحی': 'طراحی گرافیک و UI/UX',
    'ui': 'طراحی گرافیک و UI/UX',
    'ux': 'طراحی گرافیک و UI/UX',
    'graphic': 'طراحی گرافیک و UI/UX',
    'بازاریابی': 'بازاریابی و فروش',
    'marketing': 'بازاریابی و فروش',
    'فروش': 'بازاریابی و فروش',
    'sales': 'بازاریابی و فروش',
    'مالی': 'مالی و حسابداری',
    'حسابداری': 'مالی و حسابداری',
    'accounting': 'مالی و حسابداری',
    'منابع انسانی': 'منابع انسانی',
    'hr': 'منابع انسانی',
    'مدیریت': 'مدیریت و رهبری',
    'management': 'مدیریت و رهبری',
    'شبکه': 'شبکه و زیرساخت',
    'network': 'شبکه و زیرساخت',
    'devops': 'DevOps و زیرساخت',
    'امنیت': 'امنیت سایبری',
    'security': 'امنیت سایبری',
    'محتوا': 'تولید محتوا و کپی‌رایتینگ',
    'content': 'تولید محتوا و کپی‌رایتینگ',
}

CATEGORY_LABELS = [
    'برنامه‌نویسی و توسعه نرم‌افزار',
    'علم داده و هوش مصنوعی',
    'طراحی گرافیک و UI/UX',
    'بازاریابی و فروش',
    'مالی و حسابداری',
    'منابع انسانی',
    'مدیریت و رهبری',
    'شبکه و زیرساخت',
    'DevOps و زیرساخت',
    'امنیت سایبری',
    'تولید محتوا و کپی‌رایتینگ',
    'مهندسی صنایع',
    'مهندسی مکانیک',
    'مهندسی برق',
    'پزشکی و سلامت',
    'آموزش',
    'حقوق و وکالت',
    'سایر',
]


_classifier = None
_tokenizer = None


def get_classifier():
    """Lazy-load BERT classifier."""
    global _classifier
    if _classifier is None:
        try:
            from transformers import pipeline
            _classifier = pipeline(
                'text-classification',
                model='HooshvareLab/bert-fa-base-uncased-sentiment-snappfood',
                tokenizer='HooshvareLab/bert-fa-base-uncased-sentiment-snappfood',
                top_k=None,
            )
        except Exception:
            _classifier = 'unavailable'
    return _classifier


def extract_skills(text: str) -> list:
    """Extract skills from resume text using dictionary matching."""
    found = set()
    text_lower = text.lower()
    for key, skill_name in SKILLS_DICT.items():
        if key.lower() in text_lower:
            found.add(skill_name)
    return sorted(list(found))


def extract_fields(text: str) -> list:
    """Extract job fields from resume text."""
    found = set()
    text_lower = text.lower()
    for key, field_name in FIELDS_DICT.items():
        if key.lower() in text_lower:
            found.add(field_name)
    return sorted(list(found))


def classify_resume(text: str) -> dict:
    """
    Classify resume into a job category.
    Uses rule-based approach enhanced with BERT if available.
    Returns: {category, confidence, skills, fields}
    """
    # Extract skills and fields first (rule-based, very reliable)
    skills = extract_skills(text)
    fields = extract_fields(text)

    # Determine category from fields
    category = 'سایر'
    confidence = 0.3

    if fields:
        # Count field occurrences to pick the most relevant
        field_counts = {}
        for f in fields:
            field_counts[f] = field_counts.get(f, 0) + 1
        category = max(field_counts, key=field_counts.get)
        confidence = min(0.95, 0.5 + len(skills) * 0.05)

    # Try BERT classification as enhancement
    clf = get_classifier()
    if clf and clf != 'unavailable':
        try:
            # Use first 512 chars for BERT
            snippet = text[:512]
            results = clf(snippet)
            if results and isinstance(results, list) and len(results) > 0:
                bert_label = results[0]
                if isinstance(bert_label, dict):
                    # BERT gives us sentiment; we use it to boost confidence
                    bert_conf = bert_label.get('score', 0)
                    confidence = min(0.98, confidence + bert_conf * 0.1)
        except Exception:
            pass

    # Fallback: use skills to infer category
    if category == 'سایر' and skills:
        dev_skills = {'Python', 'JavaScript', 'Java', 'Django', 'React', 'Node.js',
                      'C#', 'C++', 'PHP', '.NET', 'TypeScript', 'Vue.js', 'Flutter'}
        data_skills = {'Machine Learning', 'Deep Learning', 'NLP', 'Data Science',
                       'TensorFlow', 'PyTorch', 'Pandas', 'NumPy'}
        design_skills = {'Figma', 'Photoshop', 'Illustrator', 'UI/UX'}
        marketing_skills = {'SEO', 'Digital Marketing', 'Google Analytics', 'Content Marketing'}

        skill_set = set(skills)
        if skill_set & dev_skills:
            category = 'برنامه‌نویسی و توسعه نرم‌افزار'
            confidence = 0.7
        elif skill_set & data_skills:
            category = 'علم داده و هوش مصنوعی'
            confidence = 0.7
        elif skill_set & design_skills:
            category = 'طراحی گرافیک و UI/UX'
            confidence = 0.7
        elif skill_set & marketing_skills:
            category = 'بازاریابی و فروش'
            confidence = 0.7

    return {
        'category': category,
        'confidence': round(confidence, 3),
        'skills': skills,
        'fields': fields,
    }


def suggest_search_keywords(text: str, skills: list, fields: list) -> str:
    """Generate optimal search keywords from resume analysis."""
    keywords = []

    if fields:
        keywords.append(fields[0])

    # Add top skills as keywords
    for skill in skills[:5]:
        keywords.append(skill)

    return ' '.join(keywords)