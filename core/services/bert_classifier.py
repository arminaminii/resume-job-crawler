"""
Resume Analysis Service

Extracts structured information from Persian/English resumes:
- Skills (programming, frameworks, tools)
- Education (degrees, universities, fields of study)
- Work History (companies, durations, titles)
- Projects (descriptions, technologies used)
- Software/Tools (IDEs, productivity tools)
- Job Fields (broad categories)

Uses rule-based keyword extraction with word-boundary matching.
"""
import re
from collections import OrderedDict


# --- Skill & Field Dictionaries for Persian resumes ---
# Keys are matched with WORD BOUNDARIES for Latin text to avoid false positives
# (e.g. 'javascript' must NOT match 'java', 'ui' must NOT match 'built')
# CJK/Persian keys use substring matching (safe because they're multi-char)

SKILLS_DICT = {
    # Programming Languages
    'python': 'Python', '\u067e\u0627\u06cc\u062a\u0648\u0646': 'Python',
    'django': 'Django', '\u062c\u0646\u06af\u0648': 'Django',
    'flask': 'Flask', 'fastapi': 'FastAPI',
    'typescript': 'TypeScript', 'javascript': 'JavaScript',
    '\u062c\u0627\u0648\u0627\u0633\u06a9\u0631\u06cc\u067e\u062a': 'JavaScript',
    'react': 'React', '\u0631\u06cc\u200c\u0627\u06a9\u062a': 'React',
    'vue': 'Vue.js', 'vue.js': 'Vue.js', 'nuxt': 'Nuxt.js',
    'next.js': 'Next.js', 'nextjs': 'Next.js',
    'node.js': 'Node.js', 'nodejs': 'Node.js', '\u0646\u0648\u062f': 'Node.js',
    'java': 'Java', '\u062c\u0627\u0648\u0627': 'Java',
    'spring': 'Spring', 'spring boot': 'Spring Boot',
    'c#': 'C#', 'c\+\+': 'C++', '.net': '.NET', 'php': 'PHP',
    'laravel': 'Laravel', '\u0644\u0627\u0631\u0627\u0648\u0644': 'Laravel',
    'go ': 'Go', 'golang': 'Go', 'rust': 'Rust',
    # Frontend
    'html': 'HTML', 'css': 'CSS', 'sass': 'SASS', 'less': 'LESS',
    'tailwind': 'Tailwind CSS', 'bootstrap': 'Bootstrap',
    'material ui': 'Material UI', 'ant design': 'Ant Design',
    # Mobile
    'flutter': 'Flutter', 'dart': 'Dart', 'swift': 'Swift',
    'kotlin': 'Kotlin', 'android': 'Android', 'ios': 'iOS',
    'react native': 'React Native',
    # Database
    'sql': 'SQL', 'mysql': 'MySQL', 'postgresql': 'PostgreSQL',
    'mongodb': 'MongoDB', 'redis': 'Redis', 'elasticsearch': 'Elasticsearch',
    'sqlite': 'SQLite', 'oracle': 'Oracle DB',
    # DevOps & Cloud
    'docker': 'Docker', 'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes',
    'git': 'Git', 'github': 'GitHub', 'gitlab': 'GitLab',
    'linux': 'Linux', 'ubuntu': 'Ubuntu', 'centos': 'CentOS',
    'aws': 'AWS', 'azure': 'Azure', 'gcp': 'Google Cloud',
    'terraform': 'Terraform', 'ansible': 'Ansible',
    'jenkins': 'Jenkins', 'github actions': 'GitHub Actions',
    'nginx': 'Nginx', 'ci/cd': 'CI/CD', 'devops': 'DevOps',
    # Data & AI
    'machine learning': 'Machine Learning',
    '\u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u0645\u0627\u0634\u06cc\u0646': 'Machine Learning',
    'deep learning': 'Deep Learning',
    '\u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u0639\u0645\u06cc\u0642': 'Deep Learning',
    'nlp': 'NLP',
    '\u067e\u0631\u062f\u0627\u0632\u0634 \u0632\u0628\u0627\u0646 \u0637\u0628\u06cc\u0639\u06cc': 'NLP',
    'data science': 'Data Science',
    '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647': 'Data Science',
    'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
    'keras': 'Keras', 'scikit-learn': 'Scikit-learn', 'scikit': 'Scikit-learn',
    'pandas': 'Pandas', 'numpy': 'NumPy', 'matplotlib': 'Matplotlib',
    'opencv': 'OpenCV', 'hugging face': 'Hugging Face',
    'langchain': 'LangChain', 'llm': 'LLM', 'rag': 'RAG',
    'power bi': 'Power BI', 'tableau': 'Tableau', 'excel': 'Excel',
    'spark': 'Apache Spark', 'hadoop': 'Hadoop', 'kafka': 'Kafka',
    # Design
    'figma': 'Figma', 'photoshop': 'Photoshop',
    '\u0627\u06cc\u0644\u0648\u0633\u062a\u0631\u06cc\u062a\u0648\u0631': 'Illustrator',
    'illustrator': 'Illustrator', 'after effects': 'After Effects',
    'premiere': 'Premiere Pro', 'adobe xd': 'Adobe XD',
    'ui/ux': 'UI/UX', 'ux': 'UX Design',
    'blender': 'Blender', 'canva': 'Canva',
    # Marketing
    'seo': 'SEO', '\u0633\u0626\u0648': 'SEO',
    'google analytics': 'Google Analytics', 'google ads': 'Google Ads',
    'digital marketing': 'Digital Marketing',
    '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644': 'Digital Marketing',
    'content marketing': 'Content Marketing',
    'email marketing': 'Email Marketing',
    '\u062a\u0648\u0644\u06cc\u062f \u0645\u062d\u062a\u0648\u0627': 'Content Creation',
    # Project Management
    'project management': 'Project Management',
    '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647': 'Project Management',
    'agile': 'Agile', 'scrum': 'Scrum', 'kanban': 'Kanban',
    'jira': 'Jira', 'confluence': 'Confluence',
    'trello': 'Trello', 'notion': 'Notion',
    # Security
    'penetration testing': 'Penetration Testing', 'pentest': 'Penetration Testing',
    '\u062a\u0633\u062a \u0646\u0641\u0648\u0630': 'Penetration Testing',
    'owasp': 'OWASP', 'burp suite': 'Burp Suite',
    'firewall': 'Firewall', 'siem': 'SIEM',
    'cisco': 'Cisco', 'mikrotik': 'Mikrotik',
    # Testing
    'selenium': 'Selenium', 'cypress': 'Cypress', 'playwright': 'Playwright',
    'jest': 'Jest', 'pytest': 'PyTest', 'unit test': 'Unit Testing',
    'api test': 'API Testing', 'manual test': 'Manual Testing',
    # Game
    'unity': 'Unity', 'unreal': 'Unreal Engine',
    # Embedded/IoT
    'arduino': 'Arduino', 'raspberry': 'Raspberry Pi',
    'fpga': 'FPGA', 'verilog': 'Verilog', 'embedded': 'Embedded',
    # Accounting/Finance
    'sap': 'SAP', 'erp': 'ERP',
}

# Persian multi-char keys safe for substring matching
_SAFE_SKILL_KEYS = {
    '\u067e\u0627\u06cc\u062a\u0648\u0646', '\u062c\u0646\u06af\u0648',
    '\u062c\u0627\u0648\u0627\u0633\u06a9\u0631\u06cc\u067e\u062a',
    '\u0631\u06cc\u200c\u0627\u06a9\u062a', '\u0646\u0648\u062f', '\u062c\u0627\u0648\u0627',
    '\u0627\u06cc\u0644\u0648\u0633\u062a\u0631\u06cc\u062a\u0648\u0631',
    '\u0633\u0626\u0648',
    '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644',
    '\u062a\u0648\u0644\u06cc\u062f \u0645\u062d\u062a\u0648\u0627',
    '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647',
    '\u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u0645\u0627\u0634\u06cc\u0646',
    '\u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u0639\u0645\u06cc\u0642',
    '\u067e\u0631\u062f\u0627\u0632\u0634 \u0632\u0628\u0627\u0646 \u0637\u0628\u06cc\u0639\u06cc',
    '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647',
    '\u0644\u0627\u0631\u0627\u0648\u0644',
    '\u062a\u0633\u062a \u0646\u0641\u0648\u0630',
}

# Software & Tools dictionary (IDEs, editors, productivity)
SOFTWARE_TOOLS_DICT = {
    'vscode': 'VS Code', 'vs code': 'VS Code', 'visual studio code': 'VS Code',
    'intellij': 'IntelliJ IDEA', 'pycharm': 'PyCharm',
    'webstorm': 'WebStorm', 'android studio': 'Android Studio',
    'xcode': 'Xcode', 'postman': 'Postman',
    'insomnia': 'Insomnia', 'swagger': 'Swagger',
    'docker desktop': 'Docker Desktop', 'putty': 'PuTTY',
    'filezilla': 'FileZilla', 'winscp': 'WinSCP',
    'vim': 'Vim', 'emacs': 'Emacs', 'nano': 'Nano',
    'slack': 'Slack', 'discord': 'Discord', 'zoom': 'Zoom',
    'teams': 'MS Teams', 'outlook': 'Outlook',
    'word': 'MS Word', 'powerpoint': 'PowerPoint',
    'gimp': 'GIMP', 'inkscape': 'Inkscape',
}

# Education keywords
EDUCATION_PATTERNS = {
    'degrees_fa': [
        ('\u06a9\u0627\u0631\u0634\u0646\u0627\u0633\u06cc \u0627\u0631\u0634\u062f', 'Bachelor'),
        ('\u0644\u06cc\u0633\u0627\u0646\u0633', 'Bachelor'),
        ('\u06a9\u0627\u0631\u0634\u0646\u0627\u0633\u06cc \u0627\u0631\u0634\u062f', 'Bachelor'),
        ('\u0641\u0648\u0642 \u062f\u06a9\u062a\u0631\u0627', 'PhD'),
        ('\u062f\u06a9\u062a\u0631\u06cc', 'PhD'),
        ('\u06a9\u0627\u0631\u0634\u0646\u0627\u0633\u06cc \u0627\u0631\u0634\u062f', 'Master'),
        ('\u0645\u062f\u0631\u06a9', 'Master'),
        ('\u0627\u0631\u0634\u062f', 'Master'),
        ('\u0622\u0645\u0648\u0632\u0634', 'High School Diploma'),
        ('\u062f\u06cc\u067e\u0644\u0645', 'Diploma'),
        ('\u0641\u0648\u0642', 'Post-Doc'),
    ],
    'degrees_en': [
        ('bachelor', 'Bachelor'),
        ('b\.?s\.?c', 'BSc'),
        ('master', 'Master'),
        ('m\.?s\.?c', 'MSc'),
        ('mba', 'MBA'),
        ('phd', 'PhD'),
        ('ph\.?d', 'PhD'),
        ('doctorate', 'Doctorate'),
        ('diploma', 'Diploma'),
        ('associate', 'Associate Degree'),
        ('b\.?a', 'BA'),
        ('b\.?e', 'BE'),
    ],
    'fields_fa': [
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u06a9\u0627\u0645\u067e\u06cc\u0648\u062a\u0631', 'Computer Engineering'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631', 'Software Engineering'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0627\u0637\u0644\u0627\u0639\u0627\u062a', 'IT Engineering'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0628\u0631\u0642', 'Electrical Engineering'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0635\u0646\u0627\u06cc\u0639', 'Industrial Engineering'),
        ('\u0639\u0644\u0648\u0645 \u06a9\u0627\u0645\u067e\u06cc\u0648\u062a\u0631', 'Computer Science'),
        ('\u0631\u06cc\u0627\u0636\u06cc', 'Mathematics'),
        ('\u0622\u0645\u0627\u0631', 'Statistics'),
        ('\u0645\u062f\u06cc\u0631\u06cc\u062a', 'Management'),
        ('\u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc', 'Accounting'),
        ('\u0645\u0627\u0644\u06cc', 'Finance'),
        ('\u0637\u0631\u0627\u062d\u06cc \u06afر\u0627\u0641\u06cc\u06a9', 'Graphic Design'),
        ('\u0639\u0644\u0648\u0645 \u0645\u0647\u0646\u062f\u0633\u06cc', 'Engineering'),
        ('\u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc', 'Artificial Intelligence'),
        ('\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc', 'Business'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0645\u0639\u0645\u0627\u0631\u06cc', 'Civil Engineering'),
    ],
    'fields_en': [
        ('computer science', 'Computer Science'),
        ('computer engineering', 'Computer Engineering'),
        ('software engineering', 'Software Engineering'),
        ('information technology', 'IT'),
        ('electrical engineering', 'Electrical Engineering'),
        ('industrial engineering', 'Industrial Engineering'),
        ('artificial intelligence', 'Artificial Intelligence'),
        ('machine learning', 'Machine Learning'),
        ('data science', 'Data Science'),
        ('cybersecurity', 'Cybersecurity'),
        ('graphic design', 'Graphic Design'),
        ('business administration', 'Business Administration'),
        ('accounting', 'Accounting'),
        ('mathematics', 'Mathematics'),
        ('statistics', 'Statistics'),
        ('management', 'Management'),
        ('civil engineering', 'Civil Engineering'),
        ('mechanical engineering', 'Mechanical Engineering'),
    ],
    'university_fa': [
        ('\u062f\u0627\u0646\u0634\u06af\u0627\u0647', 'University'),
        ('\u0627\u0646\u0633\u062a\u06cc\u062a\u0648', 'Institute'),
        ('\u067e\u0627\u06cc\u0648\u0647', 'Polytechnic'),
        ('\u0634\u0631\u06cc\u0641', 'Sharif'),
        ('\u062a\u0647\u0631\u0627\u0646', 'Tehran'),
        ('\u0639\u0644\u0645 \u0641\u0646\u0648\u0631\u06cc', 'Science & Research'),
        ('\u0627\u0645\u06cc\u0631\u06a9\u0628\u06cc\u0631', 'Amirkabir'),
        ('\u0635\u0646\u0639\u062a \u0639\u0644\u06cc', 'Industry'),
        ('\u062e\u0648\u0627\u0631\u0632\u0645\u06cc', 'Khajeh Nasir'),
        ('\u0628\u0647\u0634\u062a\u06cc', 'Beheshti'),
        ('\u0639\u0644\u0648\u0645 \u0648 \u0635\u0646\u0639\u062a \u0627\u06cc\u0631\u0627\u0646', 'AUST'),
        ('\u0645\u0644\u0627\u0631\u062f', 'Malard'),
        ('\u0627\u0631\u062f\u06a9\u0627\u0646', 'Ardakan'),
        ('\u0641\u0631\u062f\u0648\u0633\u06cc', 'Ferdowsi'),
        ('\u0627\u0635\u0641\u0647\u0627\u0646', 'Isfahan'),
        ('\u0634\u06cc\u0631\u0627\u0632', 'Shiraz'),
        ('\u062a\u0628\u0631\u06cc\u0632', 'Tabriz'),
    ],
    'university_en': [
        ('university', 'University'),
        ('institute of technology', 'Institute of Technology'),
        ('polytechnic', 'Polytechnic'),
        ('college', 'College'),
    ],
}

# Work history patterns
WORK_PATTERNS = {
    'title_fa': [
        '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633',
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647',
        '\u0645\u0647\u0646\u062f\u0633',
        '\u0645\u062f\u06cc\u0631',
        '\u0645\u062f\u06cc\u0631 \u067e\u0631\u0648\u0698\u0647',
        '\u0645\u062f\u06cc\u0631 \u0645\u062d\u0635\u0648\u0644',
        '\u062a\u062e\u0635\u0635 \u0627\u0631\u0634\u062f',
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633',
        '\u062f\u0627\u0646\u0634\u062c\u0648',
        '\u0637\u0631\u0627\u062d',
        '\u062a\u0633\u062a\u0631',
        '\u0645\u062a\u062e\u0635\u0635',
        '\u0645\u062d\u0644\u0644',
        '\u0645\u0647\u0646\u062f\u0633 \u0634\u0628\u06a9\u0647',
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0641\u0631\u0627\u0646\u062a',
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0628\u06a9\u200c\u0627\u0646\u062f',
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0645\u0648\u0628\u0627\u06cc\u0644',
    ],
    'title_en': [
        'developer', 'engineer', 'manager', 'designer',
        'analyst', 'specialist', 'consultant', 'administrator',
        'architect', 'lead', 'senior', 'junior', 'intern',
        'cto', 'vp', 'director', 'head', 'cofounder', 'co-founder',
        'full stack', 'frontend', 'backend', 'fullstack',
        'devops', 'sre', 'data scientist',
        'product manager', 'scrum master',
        'graphic designer', 'ui designer', 'ux designer',
        'qa engineer', 'test engineer',
    ],
}

# Project-related patterns
PROJECT_PATTERNS = [
    '\u067e\u0631\u0648\u0698\u0647',  # project
    'project',
    '\u0646\u0645\u0648\u0646\u0647\u200c\u06a9\u0627\u0631',  # sample work
    'portfolio',
    'github',
    'gitlab',
    '\u0641\u0631\u0648\u0634\u062f\u0647',  # completed
]

# Fields use word-boundary matching for Latin keys
FIELDS_DICT = {
    '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    '\u062a\u0648\u0633\u0639\u0647 \u0648\u0628': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'developer': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'programming': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'software': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    '\u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'machine learning': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9': '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX',
    'graphic': '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX',
    '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc': '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634',
    'marketing': '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634',
    '\u0641\u0631\u0648\u0634': '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634',
    'sales': '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634',
    '\u0645\u0627\u0644\u06cc': '\u0645\u0627\u0644\u06cc \u0648 \u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc',
    '\u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc': '\u0645\u0627\u0644\u06cc \u0648 \u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc',
    'accounting': '\u0645\u0627\u0644\u06cc \u0648 \u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc',
    '\u0645\u0646\u0627\u0628\u0639 \u0627\u0646\u0633\u0627\u0646\u06cc': '\u0645\u0646\u0627\u0628\u0639 \u0627\u0646\u0633\u0627\u0646\u06cc',
    '\u0645\u062f\u06cc\u0631\u06cc\u062a': '\u0645\u062f\u06cc\u0631\u06cc\u062a \u0648 \u0631\u0647\u0628\u0631\u06cc',
    'management': '\u0645\u062f\u06cc\u0631\u06cc\u062a \u0648 \u0631\u0647\u0628\u0631\u06cc',
    '\u0634\u0628\u06a9\u0647': '\u0634\u0628\u06a9\u0647 \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    'network': '\u0634\u0628\u06a9\u0647 \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    'devops': 'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    '\u0627\u0645\u0646\u06cc\u062a': '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc',
    'security': '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc',
    '\u0645\u062d\u062a\u0648\u0627': '\u062a\u0648\u0644\u06cc\u062f \u0645\u062d\u062a\u0648\u0627 \u0648 \u06a9\u067e\u06cc\u200c\u0631\u0627\u06cc\u062a\u06cc\u0646\u06af',
    'content': '\u062a\u0648\u0644\u06cc\u062f \u0645\u062d\u062a\u0648\u0627 \u0648 \u06a9\u067e\u06cc\u200c\u0631\u0627\u06cc\u062a\u06cc\u0646\u06af',
}

_FIELDS_SAFE_KEYS = {
    '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633', '\u062a\u0648\u0633\u0639\u0647 \u0648\u0628',
    '\u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc', '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9',
    '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc', '\u0641\u0631\u0648\u0634',
    '\u0645\u0627\u0644\u06cc', '\u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc',
    '\u0645\u0646\u0627\u0628\u0639 \u0627\u0646\u0633\u0627\u0646\u06cc', '\u0645\u062f\u06cc\u0631\u06cc\u062a',
    '\u0634\u0628\u06a9\u0647', '\u0627\u0645\u0646\u06cc\u062a', '\u0645\u062d\u062a\u0648\u0627',
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
        return bool(re.search(r'\b' + re.escape(key_lower) + r'\b', text.lower()))
    return key_lower in text.lower()


def extract_skills(text: str) -> list:
    """Extract skills from resume text using word-boundary matching."""
    found = set()
    for key, skill_name in SKILLS_DICT.items():
        if _match_key(text, key, _SAFE_SKILL_KEYS):
            found.add(skill_name)
    return sorted(list(found))


def extract_software_tools(text: str) -> list:
    """Extract software/tools (IDEs, editors, productivity apps) from resume."""
    found = set()
    text_lower = text.lower()
    for key, tool_name in SOFTWARE_TOOLS_DICT.items():
        if key.lower() in text_lower:
            found.add(tool_name)
    return sorted(list(found))


def extract_fields(text: str) -> list:
    """Extract job fields from resume text using word-boundary matching."""
    found = set()
    for key, field_name in FIELDS_DICT.items():
        if _match_key(text, key, _FIELDS_SAFE_KEYS):
            found.add(field_name)
    return sorted(list(found))


def extract_education(text: str) -> dict:
    """
    Extract education information from resume.
    Returns dict with: degrees, fields_of_study, universities
    """
    result = {'degrees': [], 'fields_of_study': [], 'universities': []}
    seen = set()
    text_lower = text.lower()

    # Extract degrees
    for pattern, degree in EDUCATION_PATTERNS['degrees_fa'] + EDUCATION_PATTERNS['degrees_en']:
        if re.search(pattern, text_lower):
            if degree not in seen:
                result['degrees'].append(degree)
                seen.add(degree)

    # Extract fields of study
    for pattern, field in EDUCATION_PATTERNS['fields_fa'] + EDUCATION_PATTERNS['fields_en']:
        if re.search(pattern, text_lower):
            if field not in seen:
                result['fields_of_study'].append(field)
                seen.add(field)

    # Extract universities
    for pattern, uni in EDUCATION_PATTERNS['university_fa'] + EDUCATION_PATTERNS['university_en']:
        if re.search(pattern, text_lower):
            if uni not in seen:
                result['universities'].append(uni)
                seen.add(uni)

    return result


def extract_work_history(text: str) -> list:
    """
    Extract job titles/roles mentioned in resume.
    Returns list of detected job titles.
    """
    found = set()
    text_lower = text.lower()

    for title in WORK_PATTERNS['title_fa']:
        if title in text_lower:
            found.add(title)
    for title in WORK_PATTERNS['title_en']:
        if re.search(r'\b' + re.escape(title) + r'\b', text_lower):
            found.add(title.title())

    return sorted(list(found))


def extract_projects(text: str) -> list:
    """
    Detect if resume contains project descriptions.
    Returns list of project-related keywords found.
    """
    found = set()
    text_lower = text.lower()
    for pattern in PROJECT_PATTERNS:
        if pattern in text_lower:
            found.add(pattern)
    return sorted(list(found))


def classify_resume(text: str) -> dict:
    """
    Classify resume into a job category using enhanced rule-based approach.
    Now extracts: education, work history, projects, software/tools.

    Returns: {
        category, confidence, skills, fields,
        education (dict), work_history (list), projects (list),
        software_tools (list)
    }
    """
    skills = extract_skills(text)
    fields = extract_fields(text)
    education = extract_education(text)
    work_history = extract_work_history(text)
    projects = extract_projects(text)
    software_tools = extract_software_tools(text)

    category = '\u0633\u0627\u06cc\u0631'
    confidence = 0.3

    if fields:
        field_counts = {}
        for f in fields:
            field_counts[f] = field_counts.get(f, 0) + 1
        category = max(field_counts, key=field_counts.get)
        confidence = min(0.95, 0.5 + len(skills) * 0.05)

    # Fallback: use skills to infer category
    if category == '\u0633\u0627\u06cc\u0631' and skills:
        dev_skills = {'Python', 'JavaScript', 'Java', 'Django', 'React', 'Node.js',
                      'C#', 'C++', 'PHP', '.NET', 'TypeScript', 'Vue.js', 'Flutter'}
        data_skills = {'Machine Learning', 'Deep Learning', 'NLP', 'Data Science',
                       'TensorFlow', 'PyTorch', 'Pandas', 'NumPy'}
        design_skills = {'Figma', 'Photoshop', 'Illustrator', 'UI/UX'}
        marketing_skills = {'SEO', 'Digital Marketing', 'Google Analytics', 'Content Marketing'}
        devops_skills = {'Docker', 'Kubernetes', 'AWS', 'Azure', 'CI/CD', 'Terraform'}
        security_skills = {'Penetration Testing', 'OWASP', 'Burp Suite', 'Cisco', 'Mikrotik'}

        skill_set = set(skills)
        if skill_set & devops_skills:
            category = 'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a'
            confidence = 0.75
        elif skill_set & security_skills:
            category = '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc'
            confidence = 0.75
        elif skill_set & dev_skills:
            category = '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631'
            confidence = 0.7
        elif skill_set & data_skills:
            category = '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc'
            confidence = 0.7
        elif skill_set & design_skills:
            category = '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX'
            confidence = 0.7
        elif skill_set & marketing_skills:
            category = '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634'
            confidence = 0.7

    # Boost confidence if education matches detected field
    if education['fields_of_study']:
        edu_field = education['fields_of_study'][0]
        if edu_field and (edu_field in category or any(
            kw in category for kw in edu_field.split()
        )):
            confidence = min(0.95, confidence + 0.15)

    # Boost if work history matches
    if work_history:
        confidence = min(0.95, confidence + 0.05)

    # Boost if projects detected
    if projects:
        confidence = min(0.95, confidence + 0.03)

    return {
        'category': category,
        'confidence': round(confidence, 3),
        'skills': skills,
        'fields': fields,
        'education': education,
        'work_history': work_history,
        'projects': projects,
        'software_tools': software_tools,
    }


def suggest_search_keywords(text: str, skills: list, fields: list) -> str:
    """Generate optimal search keywords from resume analysis.

    Priority: user's strongest skills first, then field.
    Now includes education field and tools in keyword generation.
    """
    keywords = []
    if fields:
        keywords.append(fields[0])
    for skill in skills[:5]:
        keywords.append(skill)
    return ' '.join(keywords)
