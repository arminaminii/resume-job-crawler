import re


# --- Skill & Field Dictionaries for Persian resumes ---
# Keys are matched with WORD BOUNDARIES for Latin text to avoid false positives
# (e.g. 'javascript' must NOT match 'java', 'ui' must NOT match 'built')
# CJK/Persian keys use substring matching (safe because they're multi-char)

# Order matters: longer/more-specific keys MUST come before shorter ones
SKILLS_DICT = {
    # Programming
    'python': 'Python', 'پایتون': 'Python',
    'django': 'Django', 'جنگو': 'Django',
    'flask': 'Flask', 'typescript': 'TypeScript',
    'react': 'React', 'ری‌اکت': 'React',
    'vue': 'Vue.js', 'node.js': 'Node.js', 'نود': 'Node.js',
    'جاواسکریپت': 'JavaScript',
    'javascript': 'JavaScript',
    'java': 'Java', 'جاوا': 'Java',
    'spring': 'Spring', 'c#': 'C#',
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
    'figma': 'Figma', 'photoshop': 'Photoshop',
    'ایلوستریتور': 'Illustrator',
    'illustrator': 'Illustrator', 'ui/ux': 'UI/UX',
    'یو‌آی': 'UI/UX',
    # Marketing
    'seo': 'SEO', 'سئو': 'SEO',
    'google analytics': 'Google Analytics',
    'digital marketing': 'Digital Marketing',
    'بازاریابی دیجیتال': 'Digital Marketing',
    'content marketing': 'Content Marketing',
    'تولید محتوا': 'Content Creation',
    # Other
    'project management': 'Project Management',
    'مدیریت پروژه': 'Project Management',
    'agile': 'Agile', 'scrum': 'Scrum', 'jira': 'Jira',
}

# CJK/Persian skill keys safe for substring matching (multi-char, no false positives)
_SAFE_SKILL_KEYS = {
    'پایتون', 'جنگو', 'جاواسکریپت',
    'ری‌اکت', 'نود', 'جاوا',
    'ایلوستریتور', 'یو‌آی',
    'سئو', 'بازاریابی دیجیتال',
    'تولید محتوا', 'مدیریت پروژه',
    'یادگیری ماشین', 'یادگیری عمیق',
    'پردازش زبان طبیعی', 'علم داده',
}

# Fields use word-boundary matching for Latin keys to avoid false positives
# Removed: 'وب', 'داده', 'ai', 'ui', 'ux', 'hr', 'data', 'content' (too short, cause false matches)
# Changed 'طراحی' -> 'طراحی گرافیک' (more specific)
FIELDS_DICT = {
    'برنامه‌نویسی': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'توسعه وب': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'developer': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'programming': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'software': 'برنامه‌نویسی و توسعه نرم‌افزار',
    'هوش مصنوعی': 'علم داده و هوش مصنوعی',
    'machine learning': 'علم داده و هوش مصنوعی',
    'طراحی گرافیک': 'طراحی گرافیک و UI/UX',
    'graphic': 'طراحی گرافیک و UI/UX',
    'بازاریابی': 'بازاریابی و فروش',
    'marketing': 'بازاریابی و فروش',
    'فروش': 'بازاریابی و فروش',
    'sales': 'بازاریابی و فروش',
    'مالی': 'مالی و حسابداری',
    'حسابداری': 'مالی و حسابداری',
    'accounting': 'مالی و حسابداری',
    'منابع انسانی': 'منابع انسانی',
    'مدیریت': 'مدیریت و رهبری',
    'management': 'مدیریت و رهبری',
    'شبکه': 'شبکه و زیرساخت',
    'network': 'شبکه و زیرساخت',
    'devops': 'DevOps و زیرساخت',
    'امنیت': 'امنیت سایبری',
    'security': 'امنیت سایبری',
    'محتوا': 'تولید محتوا و کپی‌رایتینگ',
}

# CJK/Persian field keys safe for substring matching
_FIELDS_SAFE_KEYS = {
    'برنامه‌نویسی', 'توسعه وب',
    'هوش مصنوعی', 'طراحی گرافیک',
    'بازاریابی', 'فروش',
    'مالی', 'حسابداری',
    'منابع انسانی', 'مدیریت',
    'شبکه', 'امنیت', 'محتوا',
}


def _match_key(text: str, key: str, safe_keys: set) -> bool:
    """Match key in text.

    - For CJK/Persian multi-char keys (in safe_keys): substring match
    - For ASCII/Latin keys: word-boundary regex match
    """
    key_lower = key.lower()
    if key_lower in safe_keys:
        return key_lower in text.lower()
    if key_lower.isascii():
        import re
        return bool(re.search(r'\b' + re.escape(key_lower) + r'\b', text.lower()))
    return key_lower in text.lower()


def extract_skills(text: str) -> list:
    """Extract skills from resume text using word-boundary matching."""
    found = set()
    for key, skill_name in SKILLS_DICT.items():
        if _match_key(text, key, _SAFE_SKILL_KEYS):
            found.add(skill_name)
    return sorted(list(found))


def extract_fields(text: str) -> list:
    """Extract job fields from resume text using word-boundary matching."""
    found = set()
    for key, field_name in FIELDS_DICT.items():
        if _match_key(text, key, _FIELDS_SAFE_KEYS):
            found.add(field_name)
    return sorted(list(found))


def classify_resume(text: str) -> dict:
    """Classify resume into a job category using rule-based approach.
    Returns: {category, confidence, skills, fields}
    """
    skills = extract_skills(text)
    fields = extract_fields(text)

    category = 'سایر'
    confidence = 0.3

    if fields:
        field_counts = {}
        for f in fields:
            field_counts[f] = field_counts.get(f, 0) + 1
        category = max(field_counts, key=field_counts.get)
        confidence = min(0.95, 0.5 + len(skills) * 0.05)

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
    for skill in skills[:5]:
        keywords.append(skill)
    return ' '.join(keywords)
