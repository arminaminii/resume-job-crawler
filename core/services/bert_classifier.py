"""
Resume Analysis Service

Extracts structured information from Persian/English resumes:
- Skills (programming, frameworks, tools)
- Education (degrees, universities, fields of study, GPA)
- Work History (companies, durations, titles, responsibilities)
- Projects (descriptions, technologies used, roles)
- Software/Tools (IDEs, productivity tools)
- Job Fields (broad categories)
- Experience Level (junior/mid/senior/manager)
- Contact Info (email, phone, LinkedIn)

Uses rule-based keyword extraction with word-boundary matching.
Includes enhanced matching against JobCategory tree for better suggestions.
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
    'c#': 'C#', 'c++': 'C++', '.net': '.NET', 'php': 'PHP',
    'laravel': 'Laravel', '\u0644\u0627\u0631\u0627\u0648\u0644': 'Laravel',
    'go ': 'Go', 'golang': 'Go', 'rust': 'Rust',
    # Frontend
    'html': 'HTML', 'html5': 'HTML5', 'css': 'CSS', 'css3': 'CSS3',
    'sass': 'Sass', 'scss': 'SCSS', 'less': 'Less',
    'tailwind': 'Tailwind CSS', 'bootstrap': 'Bootstrap',
    'jquery': 'jQuery', 'redux': 'Redux', 'graphql': 'GraphQL',
    'webpack': 'Webpack', 'vite': 'Vite', 'babel': 'Babel',
    # Backend
    'express': 'Express.js', 'nestjs': 'NestJS',
    'gin': 'Gin (Go)', 'fiber': 'Fiber (Go)',
    'rails': 'Ruby on Rails', 'ruby': 'Ruby',
    'sinatra': 'Sinatra', 'flask': 'Flask',
    'symfony': 'Symfony', 'codeigniter': 'CodeIgniter',
    'asp.net': 'ASP.NET', 'blazor': 'Blazor',
    # Mobile
    'flutter': 'Flutter', '\u0641\u0644\u0627\u062a\u0631': 'Flutter',
    'react native': 'React Native',
    'swift': 'Swift', 'kotlin': 'Kotlin', 'dart': 'Dart',
    'ionic': 'Ionic', 'xamarin': 'Xamarin',
    # Data & AI
    'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
    'keras': 'Keras', 'scikit': 'Scikit-learn', 'sklearn': 'Scikit-learn',
    'pandas': 'Pandas', 'numpy': 'NumPy', 'matplotlib': 'Matplotlib',
    'seaborn': 'Seaborn', 'opencv': 'OpenCV',
    'spark': 'Apache Spark', 'hadoop': 'Hadoop',
    'jupyter': 'Jupyter', 'colab': 'Google Colab',
    'tableau': 'Tableau', 'power bi': 'Power BI',
    'nlp': 'NLP', 'computer vision': 'Computer Vision',
    'llm': 'LLM', 'langchain': 'LangChain',
    'transformers': 'Transformers', 'hugging face': 'Hugging Face',
    # Database
    'sql': 'SQL', 'mysql': 'MySQL', 'postgresql': 'PostgreSQL',
    'mongodb': 'MongoDB', 'redis': 'Redis', 'elasticsearch': 'Elasticsearch',
    'sqlite': 'SQLite', 'oracle': 'Oracle DB', 'mssql': 'MSSQL',
    'cassandra': 'Cassandra', 'dynamodb': 'DynamoDB',
    'neo4j': 'Neo4j', 'supabase': 'Supabase', 'prisma': 'Prisma',
    # DevOps & Cloud
    'docker': 'Docker', 'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes',
    'jenkins': 'Jenkins', 'gitlab ci': 'GitLab CI', 'github actions': 'GitHub Actions',
    'terraform': 'Terraform', 'ansible': 'Ansible',
    'aws': 'AWS', 'azure': 'Azure', 'gcp': 'Google Cloud',
    'digitalocean': 'DigitalOcean', 'linux': 'Linux', 'nginx': 'Nginx',
    'apache': 'Apache', 'traefik': 'Traefik', 'prometheus': 'Prometheus',
    'grafana': 'Grafana', 'datadog': 'Datadog',
    # Testing
    'selenium': 'Selenium', 'cypress': 'Cypress', 'playwright': 'Playwright',
    'jest': 'Jest', 'pytest': 'PyTest', 'mocha': 'Mocha',
    'junit': 'JUnit', 'mockito': 'Mockito',
    'tdd': 'TDD', 'bdd': 'BDD',
    # Design
    'figma': 'Figma', 'photoshop': 'Photoshop', 'illustrator': 'Illustrator',
    'adobe xd': 'Adobe XD', 'sketch': 'Sketch',
    'invision': 'InVision', 'zeplin': 'Zeplin',
    'after effects': 'After Effects', 'premiere': 'Premiere Pro',
    'blender': 'Blender', 'canva': 'Canva',
    # Marketing & SEO
    'seo': 'SEO', '\u0633\u0626\u0648': 'SEO',
    'sem': 'SEM', 'google analytics': 'Google Analytics',
    'google ads': 'Google Ads', 'facebook ads': 'Facebook Ads',
    'hubspot': 'HubSpot', 'mailchimp': 'Mailchimp',
    'ahrefs': 'Ahrefs', 'semrush': 'SEMrush',
    # Security
    'owasp': 'OWASP', 'burp': 'Burp Suite',
    'wireshark': 'Wireshark', 'nmap': 'Nmap',
    'metasploit': 'Metasploit', 'kali': 'Kali Linux',
    'firewall': 'Firewall', 'siem': 'SIEM',
    'cisco': 'Cisco', 'mikrotik': 'Mikrotik',
    'penetration': 'Penetration Testing',
    # CMS
    'wordpress': 'WordPress', 'shopify': 'Shopify',
    'magento': 'Magento', 'drupal': 'Drupal',
    # Other tools
    'git': 'Git', 'github': 'GitHub', 'gitlab': 'GitLab',
    'jira': 'Jira', 'confluence': 'Confluence',
    'trello': 'Trello', 'notion': 'Notion',
    'rest api': 'REST API', 'soap': 'SOAP', 'grpc': 'gRPC',
    'microservice': 'Microservices',
    'agile': 'Agile', 'scrum': 'Scrum', 'kanban': 'Kanban',
    # Game
    'unity': 'Unity', 'unreal': 'Unreal Engine',
    # Embedded/IoT
    'arduino': 'Arduino', 'raspberry': 'Raspberry Pi',
    'fpga': 'FPGA', 'verilog': 'Verilog', 'embedded': 'Embedded',
    # Accounting/Finance
    'sap': 'SAP', 'erp': 'ERP',
    'excel': 'MS Excel', 'powerpivot': 'Power Pivot',
    # Communication
    'slack': 'Slack', 'discord': 'Discord', 'zoom': 'Zoom',
    'teams': 'MS Teams', 'outlook': 'Outlook',
    # AI/ML Persian
    '\u0645\u0627\u0634\u06cc\u0646 \u0644\u0631\u0646\u06cc\u0646\u06af': 'Machine Learning',
    '\u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u0645\u0627\u0634\u06cc\u0646': 'Machine Learning',
    '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647': 'Data Science',
    '\u067e\u0631\u062f\u0627\u0632\u0634 \u0632\u0628\u0627\u0646 \u0637\u0628\u06cc\u0639\u06cc': 'NLP',
    '\u0628\u0627\u0632\u06cc\u0627\u0628\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644': 'Digital Marketing',
    '\u062a\u0648\u0644\u06cc\u062f \u0645\u062d\u062a\u0648\u0627': 'Content Marketing',
    '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647': 'Project Management',
    '\u062a\u0633\u062a \u0646\u0641\u0648\u0630': 'Penetration Testing',
    '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc': 'Cybersecurity',
    # Additional Persian tech terms
    '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0641\u0631\u0627\u0646\u062a': 'Frontend Developer',
    '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0628\u06a9\u200c\u0627\u0646\u062f': 'Backend Developer',
    '\u0641\u0648\u0644 \u0627\u0633\u062a\u06a9': 'Full Stack',
    '\u062f\u06cc\u0627\u062f\u0648\u06a9': 'Docker',
    '\u0628\u0627\u06a9\u200c\u0627\u0646\u062f': 'Backend',
    '\u0641\u0631\u0627\u0646\u062a\u200c\u0627\u0646\u062f': 'Frontend',
    '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633': 'Programmer',
    '\u0627\u06cc\u0644\u0633\u062a\u0631\u06cc\u062a\u0648\u0631': 'Illustrator',
    '\u0633\u06cc\u0633\u062a\u0645': 'Systems',
}

# Persian multi-char keys safe for substring matching
_SAFE_SKILL_KEYS = {
    '\u067e\u0627\u06cc\u062a\u0648\u0646', '\u062c\u0646\u06af\u0648',
    '\u062c\u0627\u0648\u0627\u0633\u06a9\u0631\u06cc\u067e\u062a',
    '\u0631\u06cc\u200c\u0627\u06a9\u062a', '\u0646\u0648\u062f', '\u062c\u0627\u0648\u0627',
    '\u0627\u06cc\u0644\u0648\u0633\u062a\u0631\u06cc\u062a\u0648\u0631',
    '\u0633\u0626\u0648', '\u0641\u0644\u0627\u062a\u0631', '\u0644\u0627\u0631\u0627\u0648\u0644',
    '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644',
    '\u062a\u0648\u0644\u06cc\u062f \u0645\u062d\u062a\u0648\u0627',
    '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647',
    '\u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u0645\u0627\u0634\u06cc\u0646',
    '\u0645\u0627\u0634\u06cc\u0646 \u0644\u0631\u0646\u06cc\u0646\u06af',
    '\u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u0639\u0645\u06cc\u0642',
    '\u067e\u0631\u062f\u0627\u0632\u0634 \u0632\u0628\u0627\u0646 \u0637\u0628\u06cc\u0639\u06cc',
    '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647', '\u062a\u0633\u062a \u0646\u0641\u0648\u0630',
    '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc',
    '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0641\u0631\u0627\u0646\u062a',
    '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0628\u06a9\u200c\u0627\u0646\u062f',
    '\u0641\u0648\u0644 \u0627\u0633\u062a\u06a9', '\u062f\u06cc\u0627\u062f\u0648\u06a9',
    '\u0628\u0627\u06a9\u200c\u0627\u0646\u062f', '\u0641\u0631\u0627\u0646\u062a\u200c\u0627\u0646\u062f',
    '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633', '\u0633\u06cc\u0633\u062a\u0645',
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
    'gimp': 'GIMP', 'inkscape': 'Inkscape',
}

# Education keywords
EDUCATION_PATTERNS = {
    'degrees_fa': [
        ('\u06a9\u0627\u0631\u0634\u0646\u0627\u0633\u06cc \u0627\u0631\u0634\u062f', 'Bachelor'),
        ('\u0644\u06cc\u0633\u0627\u0646\u0633', 'Bachelor'),
        ('\u0641\u0648\u0642 \u0644\u06cc\u0633\u0627\u0646\u0633', 'Bachelor'),
        ('\u06a9\u0627\u0631\u0634\u0646\u0627\u0633\u06cc', 'Bachelor'),
        ('\u0641\u0648\u0642 \u062f\u06a9\u062a\u0631\u0627', 'PhD'),
        ('\u062f\u06a9\u062a\u0631\u06cc', 'PhD'),
        ('\u06a9\u0627\u0631\u0634\u0646\u0627\u0633\u06cc \u0627\u0631\u0634\u062f', 'Master'),
        ('\u0645\u062f\u0631\u06a9', 'Master'),
        ('\u0627\u0631\u0634\u062f', 'Master'),
        ('\u0641\u0648\u0642 \u062f\u06cc\u067e\u0644\u0645', 'Associate Degree'),
        ('\u0622\u0645\u0648\u0632\u0634', 'High School Diploma'),
        ('\u062f\u06cc\u067e\u0644\u0645', 'Diploma'),
        ('\u0641\u0648\u0642', 'Post-Doc'),
    ],
    'degrees_en': [
        ('bachelor', 'Bachelor'),
        (r'b\.?s\.?c', 'BSc'),
        ('master', 'Master'),
        (r'm\.?s\.?c', 'MSc'),
        ('mba', 'MBA'),
        ('phd', 'PhD'),
        (r'ph\.?d', 'PhD'),
        ('doctorate', 'Doctorate'),
        ('diploma', 'Diploma'),
        ('associate', 'Associate Degree'),
        (r'b\.?a', 'BA'),
        (r'b\.?e', 'BE'),
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
        ('\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9', 'Graphic Design'),
        ('\u0639\u0644\u0648\u0645 \u0645\u0647\u0646\u062f\u0633\u06cc', 'Engineering'),
        ('\u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc', 'Artificial Intelligence'),
        ('\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc', 'Business'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0645\u0639\u0645\u0627\u0631\u06cc', 'Civil Engineering'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0645\u06a9\u0627\u0646\u06cc\u06a9', 'Mechanical Engineering'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0634\u06cc\u0645\u06cc', 'Chemical Engineering'),
        ('\u0639\u0644\u0648\u0645 \u0627\u0646\u0641\u0648\u0631\u0645\u0627\u062a\u06cc\u06a9', 'Information Systems'),
        ('\u0639\u0644\u0648\u0645 \u067e\u0627\u06cc\u0647', 'Basic Sciences'),
        ('\u062d\u0642\u0648\u0642', 'Law'),
        ('\u067e\u0632\u0634\u06a9\u06cc', 'Medicine'),
        ('\u0645\u0647\u0646\u062f\u0633\u06cc \u0637\u0628\u0642\u0647 \u0628\u0646\u062f\u06cc', 'Urban Planning'),
        ('\u0645\u0639\u0645\u0627\u0631\u06cc', 'Architecture'),
        ('\u0647\u0646\u0631', 'Art'),
        ('\u0627\u0642\u062a\u0635\u0627\u062f', 'Economics'),
        ('\u0631\u0648\u0627\u0628\u0637 \u0639\u0645\u0648\u0645\u06cc', 'Public Relations'),
        ('\u0639\u0644\u0648\u0645 \u0627\u0631\u062a\u0628\u0627\u0637\u0627\u062a', 'Communications'),
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
        ('chemical engineering', 'Chemical Engineering'),
        ('architecture', 'Architecture'),
        ('economics', 'Economics'),
        ('law', 'Law'),
        ('medicine', 'Medicine'),
        ('urban planning', 'Urban Planning'),
    ],
    'university_fa': [
        ('\u062f\u0627\u0646\u0634\u06af\u0627\u0647', 'University'),
        ('\u0627\u0646\u0633\u062a\u06cc\u062a\u0648', 'Institute'),
        ('\u067e\u0627\u06cc\u0648\u0647', 'Polytechnic'),
        ('\u0634\u0631\u06cc\u0641', 'Sharif'),
        ('\u062a\u0647\u0631\u0627\u0646', 'Tehran'),
        ('\u0639\u0644\u0645 \u0648 \u0635\u0646\u0639\u062a', 'AUST'),
        ('\u0627\u0645\u06cc\u0631\u06a9\u0628\u06cc\u0631', 'Amirkabir'),
        ('\u0635\u0646\u0639\u062a \u0639\u0644\u06cc', 'Azerbaijan Shahid Madani'),
        ('\u062e\u0648\u0627\u0631\u0632\u0645\u06cc', 'Khajeh Nasir'),
        ('\u0628\u0647\u0634\u062a\u06cc', 'Beheshti (Shahid)'),
        ('\u0639\u0644\u0648\u0645 \u0648 \u0635\u0646\u0639\u062a \u0627\u06cc\u0631\u0627\u0646', 'Iran University of Science and Technology'),
        ('\u0645\u0644\u0627\u0631\u062f', 'Malard'),
        ('\u0627\u0631\u062f\u06a9\u0627\u0646', 'Ardakan'),
        ('\u0641\u0631\u062f\u0648\u0633\u06cc', 'Ferdowsi (Mashhad)'),
        ('\u0627\u0635\u0641\u0647\u0627\u0646', 'Isfahan'),
        ('\u0634\u06cc\u0631\u0627\u0632', 'Shiraz'),
        ('\u062a\u0628\u0631\u06cc\u0632', 'Tabriz'),
        ('\u062a\u0647\u0631\u0627\u0646 \u062c\u0646\u0648\u0628', 'Tehran South'),
        ('\u062e\u0631\u0627\u0632\u0645\u06cc', 'Kharazmi'),
        ('\u0639\u0644\u0648\u0645 \u062a\u062d\u0642\u06cc\u0642\u0627\u062a', 'Iran University of Science and Research'),
        ('\u0633\u0645\u0646\u0627\u0646', 'Semnan'),
        ('\u0634\u0647\u06cc\u062f \u0628\u0647\u0634\u062a\u06cc', 'Shahid Beheshti'),
        ('\u0627\u06cc\u062a\u0627\u0644\u06cc\u0627\u06cc\u0627', 'Islamic Azad'),
        ('\u067e\u06cc\u0627\u0645 \u0646\u0648\u0631', 'Payame Noor'),
        ('\u0622\u0632\u0627\u062f \u0627\u0633\u0644\u0627\u0645\u06cc', 'Islamic Azad'),
        ('\u0634\u0631\u06cc\u0641 \u062a\u06a9\u0646\u0648\u0644\u0648\u0698\u06cc', 'Sharif University of Technology'),
    ],
    'university_en': [
        ('university', 'University'),
        ('institute of technology', 'Institute of Technology'),
        ('polytechnic', 'Polytechnic'),
        ('college', 'College'),
        ('sharif', 'Sharif University of Technology'),
        ('university of tehran', 'University of Tehran'),
        ('amirkabir', 'Amirkabir University of Technology'),
        ('ferdowsi', 'Ferdowsi University of Mashhad'),
        ('isfehan', 'University of Isfahan'),
        ('shiraz university', 'Shiraz University'),
        ('tabriz university', 'University of Tabriz'),
    ],
}

# Work history patterns - comprehensive titles
WORK_PATTERNS = {
    'title_fa': [
        '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633',  # programmer
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647',  # developer
        '\u0645\u0647\u0646\u062f\u0633',  # engineer
        '\u0645\u062f\u06cc\u0631',  # manager
        '\u0645\u062f\u06cc\u0631 \u067e\u0631\u0648\u0698\u0647',  # project manager
        '\u0645\u062f\u06cc\u0631 \u0645\u062d\u0635\u0648\u0644',  # product manager
        '\u062a\u062e\u0635\u0635 \u0627\u0631\u0634\u062f',  # senior specialist
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633',  # expert
        '\u062f\u0627\u0646\u0634\u062c\u0648',  # student
        '\u0637\u0631\u0627\u062d',  # designer
        '\u062a\u0633\u062a\u0631',  # tester
        '\u0645\u062a\u062e\u0635\u0635',  # specialist
        '\u0645\u062d\u0644\u0644',  # analyst
        '\u0645\u0647\u0646\u062f\u0633 \u0634\u0628\u06a9\u0647',  # network engineer
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0641\u0631\u0627\u0646\u062a',  # frontend dev
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0628\u06a9\u200c\u0627\u0646\u062f',  # backend dev
        '\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647 \u0645\u0648\u0628\u0627\u06cc\u0644',  # mobile dev
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633 \u0641\u0631\u0648\u0634',  # sales expert
        '\u0648\u06a9\u06cc\u0644',  # lawyer
        '\u0645\u0634\u0627\u0648\u0631 \u062d\u0642\u0648\u0642\u06cc',  # legal consultant
        '\u067e\u0631\u0633\u062a\u0627\u0631',  # nurse
        '\u06a9\u0627\u0631\u0622\u0645\u0648\u0632',  # intern
        '\u0645\u0631\u0628\u06cc',  # teacher
        '\u0633\u0631\u067e\u0631\u0633\u062a',  # supervisor
        '\u0645\u062f\u06cc\u0631 \u0639\u0627\u0645\u0644',  # CEO
        '\u0645\u062f\u06cc\u0631 \u0628\u0627\u0632\u0631\u06af\u0627\u0646\u06cc',  # commercial manager
        '\u0645\u062f\u06cc\u0631 \u0639\u0645\u0644\u06cc\u0627\u062a',  # operations manager
        '\u0646\u0627\u0638\u0631',  # supervisor/inspector
        '\u062a\u062d\u0644\u06cc\u0644\u06af\u0631 \u062f\u0627\u062f\u0647',  # data analyst
        '\u0637\u0631\u0627\u062d \u0631\u0627\u0628\u0637',  # UI designer
        '\u062a\u06a9\u0646\u0633\u06cc\u0646 \u0633\u062e\u062a\u200c\u0627\u0641\u0632\u0627\u0631',  # hardware tech
        '\u0627\u067e\u0631\u0627\u062a\u0648\u0631 \u0627\u0646\u0628\u0627\u0631',  # warehouse operator
        '\u062d\u0633\u0627\u0628\u062f\u0627\u0631',  # accountant
        '\u0646\u0648\u06cc\u0633\u0646\u062f\u0647',  # writer
        '\u062e\u0628\u0631\u0646\u06af\u0627\u0631',  # journalist
        '\u0639\u06a9\u0627\u0633',  # photographer
        '\u0645\u0647\u0646\u062f\u0633 \u0641\u0631\u0627\u06cc\u0646\u062f',  # process engineer
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633 \u0645\u0646\u0627\u0628\u0639 \u0627\u0646\u0633\u0627\u0646\u06cc',  # HR expert
        '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628',  # marketer
        '\u062a\u062f\u0627\u0631\u06a9\u0627\u062a',  # procurement
        '\u067e\u0634\u062a\u06cc\u0628\u0627\u0646',  # support
        '\u0628\u0631\u0642\u200c\u06a9\u0627\u0631',  # electrician
        '\u062a\u06a9\u0646\u0633\u06cc\u0646 \u0628\u0631\u0642',  # electrical tech
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633 \u0627\u062f\u0627\u0631\u06cc',  # admin expert
        '\u0645\u0646\u0634\u06cc',  # secretary
        '\u0645\u0647\u0646\u062f\u0633 \u0635\u0646\u0627\u06cc\u0639',  # industrial engineer
        '\u062a\u062f\u0631\u06cc\u0633',  # teaching
        '\u0627\u0633\u062a\u0627\u062f \u062f\u0627\u0646\u0634\u06af\u0627\u0647',  # university professor
        '\u0645\u062a\u062e\u0635\u0635 \u0641\u0631\u0648\u0634',  # sales specialist
        '\u0645\u062f\u06cc\u0631 \u0641\u0631\u0648\u0634',  # sales manager
        '\u0633\u0631\u067e\u0631\u0633\u062a \u0641\u0631\u0648\u0634',  # sales supervisor
        '\u0646\u0645\u0627\u06cc\u0646\u062f\u0647 \u0641\u0631\u0648\u0634',  # sales rep
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633 \u062a\u0648\u0644\u06cc\u062f',  # production expert
        '\u0633\u0631\u067e\u0631\u0633\u062a \u062a\u0648\u0644\u06cc\u062f',  # production supervisor
        '\u062a\u062d\u0644\u06cc\u0644\u06af\u0631 \u0633\u06cc\u0633\u062a\u0645',  # system analyst
        '\u0627\u062f\u0645\u06cc\u0646 \u0633\u06cc\u0633\u062a\u0645',  # system admin
        '\u0645\u0647\u0646\u062f\u0633 \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc',  # support engineer
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633 \u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc',  # marketing expert
        '\u0645\u0647\u0646\u062f\u0633 \u0628\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc',  # packaging engineer
        '\u0645\u0647\u0646\u062f\u0633 \u062f\u06cc\u062a\u0627',  # data engineer
        '\u062f\u0627\u0646\u0634\u0645\u0646\u062f \u062f\u0627\u062f\u0647',  # data scientist
        '\u0645\u0647\u0646\u062f\u0633 \u0627\u0645\u0646\u06cc\u062a',  # security engineer
        '\u0645\u062f\u06cc\u0631 \u062a\u06a9\u0646\u0648\u0644\u0648\u0698\u06cc',  # CTO
        '\u0645\u0639\u0627\u0631\u0641 \u0628\u0631\u0646\u062f',  # UX researcher
        '\u0645\u062d\u0644\u0644 \u0628\u06cc\u0632\u06cc\u0646\u0633',  # business analyst
        '\u0645\u062f\u06cc\u0631 \u0645\u062d\u062a\u0648\u0627',  # content manager
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633 \u0645\u062d\u062a\u0648\u0627',  # content expert
        '\u0637\u0631\u0627\u062d \u062a\u062c\u0631\u0628\u0647 \u06a9\u0627\u0631\u0628\u0631\u06cc',  # UX designer
        '\u0645\u0647\u0646\u062f\u0633 \u0627\u0637\u0644\u0627\u0639\u0627\u062a',  # IT engineer
        '\u0645\u062f\u06cc\u0631 \u0645\u0646\u0627\u0628\u0639 \u0627\u0646\u0633\u0627\u0646\u06cc',  # HR manager
        '\u0645\u0633\u0626\u0648\u0644 \u0641\u0631\u0648\u0634',  # sales representative
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
        'business analyst', 'data analyst', 'data engineer',
        'security engineer', 'system administrator', 'sysadmin',
        'content manager', 'content strategist',
        'hr manager', 'recruiter', 'talent acquisition',
        'sales manager', 'account manager',
        'technical lead', 'team lead', 'tech lead',
        'solutions architect', 'cloud architect',
        'machine learning engineer', 'ml engineer',
        'mobile developer', 'ios developer', 'android developer',
        'frontend developer', 'backend developer',
    ],
}

# Experience level detection patterns
EXPERIENCE_LEVELS = {
    'junior': [
        'junior', 'juniior', 'jnr', 'entry-level', 'entry level',
        '\u062c\u0648\u0646\u06cc\u0648\u0631', '\u0645\u0628\u062a\u062f\u06cc',
        '\u06a9\u0627\u0631\u0622\u0645\u0648\u0632', 'intern', 'trainee',
        'fresher', 'graduate', '\u062a\u0627\u0632\u0647 \u06a9\u0627\u0631',
        '\u0628\u06cc \u062a\u062c\u0631\u0628\u0647', '0-2 years', '0-1 years',
        '\u062a\u062d\u0635\u06cc\u0644\u0627\u062a \u0646\u0648\u06cc\u0646',
    ],
    'mid': [
        'mid-level', 'mid level', 'intermediate',
        '\u0645\u06cc\u0627\u0646\u200c\u0631\u062f\u0647', '\u0645\u062a\u062e\u0635\u0635',
        '\u06a9\u0627\u0631\u0634\u0646\u0627\u0633', '2-5 years', '3-5 years',
        '\u062a\u062c\u0631\u0628\u0647 \u06a9\u0627\u0631\u06cc \u0645\u062a\u0648\u0633\u0637',
    ],
    'senior': [
        'senior', 'sr.', 'sr ', 'lead', 'principal', 'expert',
        '\u0627\u0631\u0634\u062f', '\u0633\u0646\u06cc\u0648\u0631', '\u062a\u062e\u0635\u0635 \u0627\u0631\u0634\u062f',
        '5-10 years', '7+ years', '5+ years',
        '\u062a\u062c\u0631\u0628\u0647 \u06a9\u0627\u0631\u06cc \u0628\u0627\u0644\u0627',
    ],
    'manager': [
        'manager', 'director', 'head', 'vp', 'cto', 'cfo', 'coo',
        '\u0645\u062f\u06cc\u0631', '\u0633\u0631\u067e\u0631\u0633\u062a', '\u0645\u0639\u0627\u0648\u0646',
        '\u0631\u0626\u06cc\u0633', '10+ years', '8+ years',
        '\u0645\u062f\u06cc\u0631\u06cc\u062a \u062a\u06cc\u0645',
    ],
}

# Company name patterns for extraction
COMPANY_PATTERNS_FA = [
    '\u0634\u0631\u06a9\u062a',  # company
    '\u0633\u0627\u0632\u0645\u0627\u0646',  # organization
    '\u0645\u0648\u0633\u0633\u0647',  # institute
    '\u0622\u0645\u0648\u0632\u0634\u06af\u0627\u0647',  # training center
    '\u0627\u0633\u062a\u0627\u0631\u062a\u0627\u067e',  # startup
    '\u0641\u0627\u0628\u062a\u06a9',  # startup
]

# Duration patterns for work history
DURATION_PATTERNS = [
    r'(\d+)\s*(year|years|\u0633\u0627\u0644)',
    r'(\d+)\s*(month|months|\u0645\u0627\u0647)',
    r'(\d{4})\s*[-\u2013]\s*(\d{4})',  # 2019 - 2022
    r'(\d{4})\s*[-\u2013]\s*\u0627\u06a9\u0646\u0648\u0646',  # 2020 - \u0627\u06a9\u0646\u0648\u0646
]

# Project-related patterns
PROJECT_PATTERNS = [
    '\u067e\u0631\u0648\u0698\u0647',  # project
    'project',
    '\u0646\u0645\u0648\u0646\u0647\u200c\u06a9\u0627\u0631',  # sample work
    'portfolio',
    'github.com',
    'gitlab.com',
    '\u0641\u0631\u0648\u0634\u062f\u0647',  # completed
    '\u0627\u0646\u062c\u0627\u0645 \u0634\u062f\u0647',  # completed
    'side project',
    '\u067e\u0631\u0648\u0698\u0647 \u0647\u0627\u06cc',  # projects
    '\u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631',  # portfolio
]

# Contact info patterns
CONTACT_PATTERNS = {
    'email': [
        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    ],
    'phone_fa': [
        r'0?9[0-9]{9}',
        r'\u06f0\u06f9[0-9\u06f0-\u06f9]{9}',
    ],
    'phone_en': [
        r'\+98[0-9]{10}',
        r'98[0-9]{10}',
    ],
    'linkedin': [
        r'linkedin\.com/in/[a-zA-Z0-9\-]+',
    ],
    'github_url': [
        r'github\.com/[a-zA-Z0-9\-]+',
    ],
    'website': [
        r'(?:https?://)?[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/[a-zA-Z0-9\-/]*)?',
    ],
}

# Industry patterns (mapping keywords to industry sectors)
INDUSTRY_PATTERNS = {
    # Tech
    'fintech': '\u0641\u06cc\u0646\u062a\u06a9',
    'e-commerce': '\u0641\u0631\u0648\u0634\u06af\u0627\u0647 \u0627\u06cc\u0646\u062a\u0631\u0646\u062a\u06cc',
    'saas': 'SaaS',
    'edtech': '\u0641\u0646\u0627\u0648\u0631\u06cc \u0622\u0645\u0648\u0632\u0634\u06cc',
    'healthtech': '\u0641\u0646\u0627\u0648\u0631\u06cc \u0628\u0647\u062f\u0627\u0634\u062a',
    'adtech': 'AdTech',
    'gaming': '\u0628\u0627\u0632\u06cc \u0648 \u0633\u0631\u06af\u0631\u0645\u06cc',
    # Traditional
    '\u0628\u0627\u0646\u06a9': '\u0628\u0627\u0646\u06a9\u062f\u0627\u0631\u06cc',
    '\u0628\u06cc\u0645\u0647': '\u0628\u06cc\u0645\u0647',
    '\u0646\u0641\u062a': '\u0646\u0641\u062a \u0648 \u06af\u0627\u0632',
    '\u062e\u0648\u062f\u0631\u0648': '\u062e\u0648\u062f\u0631\u0648\u0633\u0627\u0632\u06cc',
    '\u062f\u0627\u0631\u0648': '\u062f\u0627\u0631\u0648\u0633\u0627\u0632\u06cc',
    '\u0641\u0648\u0644\u0627\u062f': '\u0641\u0644\u0627\u062f\u06cc',
    '\u0633\u062e\u0646': '\u0633\u062e\u0646',
}

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
    'ui/ux': '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX',
    'ux': '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX',
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
    'data science': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'cybersecurity': '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc',
    'product manager': '\u0645\u062f\u06cc\u0631\u06cc\u062a \u0645\u062d\u0635\u0648\u0644',
    '\u0645\u062f\u06cc\u0631 \u0645\u062d\u0635\u0648\u0644': '\u0645\u062f\u06cc\u0631\u06cc\u062a \u0645\u062d\u0635\u0648\u0644',
    'project manager': '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647',
    '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647': '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647',
}

_FIELDS_SAFE_KEYS = {
    '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633', '\u062a\u0648\u0633\u0639\u0647 \u0648\u0628',
    '\u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc', '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9',
    '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc', '\u0641\u0631\u0648\u0634',
    '\u0645\u0627\u0644\u06cc', '\u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc',
    '\u0645\u0646\u0627\u0628\u0639 \u0627\u0646\u0633\u0627\u0646\u06cc', '\u0645\u062f\u06cc\u0631\u06cc\u062a',
    '\u0634\u0628\u06a9\u0647', '\u0627\u0645\u0646\u06cc\u062a', '\u0645\u062d\u062a\u0648\u0627',
    '\u0645\u062f\u06cc\u0631 \u0645\u062d\u0635\u0648\u0644', '\u0645\u062f\u06cc\u0631\u06cc\u062a \u067e\u0631\u0648\u0698\u0647',
}

# --- Skill category mapping for better field inference ---
SKILL_TO_FIELD_MAP = {
    # Backend
    'Python': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'JavaScript': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'Java': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'TypeScript': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'Django': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'React': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    'Node.js': '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631',
    # Data/AI
    'Machine Learning': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'Deep Learning': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'TensorFlow': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'PyTorch': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'NLP': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'Data Science': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'Pandas': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    'NumPy': '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc',
    # Design
    'Figma': '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX',
    'Photoshop': '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX',
    'UI/UX': '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX',
    # DevOps
    'Docker': 'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    'Kubernetes': 'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    'AWS': 'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    'CI/CD': 'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    'Terraform': 'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a',
    # Security
    'Penetration Testing': '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc',
    'OWASP': '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc',
    'Burp Suite': '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc',
    # Marketing
    'SEO': '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634',
    'Digital Marketing': '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634',
    'Google Analytics': '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634',
    'Content Marketing': '\u062a\u0648\u0644\u06cc\u062f \u0645\u062d\u062a\u0648\u0627 \u0648 \u06a9\u067e\u06cc\u200c\u0631\u0627\u06cc\u062a\u06cc\u0646\u06af',
    # Finance
    'SAP': '\u0645\u0627\u0644\u06cc \u0648 \u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc',
    'ERP': '\u0645\u0627\u0644\u06cc \u0648 \u062d\u0633\u0627\u0628\u062f\u0627\u0631\u06cc',
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
    Returns dict with: degrees, fields_of_study, universities, gpa
    """
    result = {'degrees': [], 'fields_of_study': [], 'universities': [], 'gpa': None}
    seen = set()
    text_lower = text.lower()

    # Extract degrees (ordered: PhD > Master > Bachelor > others)
    degree_order = {'PhD': 0, 'Doctorate': 1, 'Post-Doc': 2, 'MBA': 3,
                     'Master': 4, 'MSc': 5, 'Bachelor': 6, 'BSc': 7, 'BA': 8,
                     'BE': 9, 'Associate Degree': 10, 'Diploma': 11,
                     'High School Diploma': 12}
    degrees_found = []
    for pattern, degree in EDUCATION_PATTERNS['degrees_fa'] + EDUCATION_PATTERNS['degrees_en']:
        if re.search(pattern, text_lower) and degree not in seen:
            degrees_found.append(degree)
            seen.add(degree)
    # Sort by degree level (highest first)
    degrees_found.sort(key=lambda d: degree_order.get(d, 99))
    result['degrees'] = degrees_found

    # Extract fields of study
    for pattern, field in EDUCATION_PATTERNS['fields_fa'] + EDUCATION_PATTERNS['fields_en']:
        if re.search(pattern, text_lower) and field not in seen:
            result['fields_of_study'].append(field)
            seen.add(field)

    # Extract universities
    for pattern, uni in EDUCATION_PATTERNS['university_fa'] + EDUCATION_PATTERNS['university_en']:
        if re.search(pattern, text_lower) and uni not in seen:
            result['universities'].append(uni)
            seen.add(uni)

    # Extract GPA
    gpa_patterns = [
        r'gpa\s*[:\s]*([\d.]+)',
        r'm\u06cc\u0627\u0646\u06af\u06cc\u0646\s*[:\s]*([\d.]+)',
        r'(?:\u0645\u06cc\u0627\u0646\u06af\u06cc\u0646|average)\s*[:\s]*([\d.]+)',
    ]
    for pat in gpa_patterns:
        m = re.search(pat, text_lower)
        if m:
            try:
                gpa_val = float(m.group(1))
                if 0 <= gpa_val <= 4.5:
                    result['gpa'] = gpa_val
                    break
            except ValueError:
                pass

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


def extract_companies(text: str) -> list:
    """
    Extract company/organization names from resume.
    Looks for lines containing company-related Persian keywords.
    Returns list of company name strings.
    """
    companies = set()
    lines = text.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        for pattern in COMPANY_PATTERNS_FA:
            idx = line_stripped.find(pattern)
            if idx >= 0:
                # Extract the company name (the line or surrounding context)
                company = line_stripped.strip()
                if len(company) > 100:
                    company = company[:100]
                if company:
                    companies.add(company)
                break
    return sorted(list(companies))


def extract_durations(text: str) -> list:
    """
    Extract work duration information from resume.
    Returns list of duration strings found.
    """
    durations = []
    seen = set()
    for pattern in DURATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if isinstance(m, tuple):
                dur = ' - '.join(str(x) for x in m)
            else:
                dur = str(m)
            if dur not in seen:
                durations.append(dur)
                seen.add(dur)
    return durations


def extract_experience_level(text: str, skills: list, work_history: list) -> str:
    """
    Detect experience level from resume text and metadata.
    Returns: 'junior', 'mid', 'senior', 'manager', or 'unknown'.
    Uses multiple signals: explicit keywords, number of skills, work titles.
    """
    text_lower = text.lower()
    scores = {'junior': 0, 'mid': 0, 'senior': 0, 'manager': 0}

    # Check explicit level keywords
    for level, patterns in EXPERIENCE_LEVELS.items():
        for pat in patterns:
            if pat.lower() in text_lower:
                scores[level] += 2

    # Check work history titles for level hints
    senior_titles = {'senior', 'lead', 'principal', 'architect', 'expert',
                     '\u0627\u0631\u0634\u062f', '\u0633\u0646\u06cc\u0648\u0631'}
    manager_titles = {'manager', 'director', 'head', 'vp', 'cto', 'cfo',
                      '\u0645\u062f\u06cc\u0631', '\u0633\u0631\u067e\u0631\u0633\u062a', '\u0631\u0626\u06cc\u0633'}
    junior_titles = {'junior', 'intern', 'trainee', 'fresher',
                     '\u062c\u0648\u0646\u06cc\u0648\u0631', '\u06a9\u0627\u0631\u0622\u0645\u0648\u0632', '\u0645\u0628\u062a\u062f\u06cc'}

    for title in work_history:
        title_lower = title.lower()
        if any(t in title_lower for t in senior_titles):
            scores['senior'] += 3
        if any(t in title_lower for t in manager_titles):
            scores['manager'] += 3
        if any(t in title_lower for t in junior_titles):
            scores['junior'] += 3

    # Use skill count as a signal
    skill_count = len(skills)
    if skill_count <= 3:
        scores['junior'] += 1
    elif skill_count <= 7:
        scores['mid'] += 1
    elif skill_count <= 12:
        scores['senior'] += 1
    else:
        scores['senior'] += 2

    # Find the level with the highest score
    best_level = max(scores, key=scores.get)
    if scores[best_level] == 0:
        return 'unknown'
    return best_level


def extract_contact_info(text: str) -> dict:
    """
    Extract contact information from resume.
    Returns dict with: email, phone, linkedin, github, website
    """
    result = {'email': '', 'phone': '', 'linkedin': '', 'github': '', 'website': ''}

    # Email
    for pat in CONTACT_PATTERNS['email']:
        m = re.search(pat, text)
        if m:
            result['email'] = m.group(0)
            break

    # Phone
    for pat in CONTACT_PATTERNS['phone_fa'] + CONTACT_PATTERNS['phone_en']:
        m = re.search(pat, text)
        if m:
            result['phone'] = m.group(0)
            break

    # LinkedIn
    for pat in CONTACT_PATTERNS['linkedin']:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result['linkedin'] = m.group(0)
            break

    # GitHub URL
    for pat in CONTACT_PATTERNS['github_url']:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result['github'] = m.group(0)
            break

    # Website (only if not already captured as github/linkedin)
    for pat in CONTACT_PATTERNS['website']:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            url = m.group(0)
            if 'github.com' not in url and 'linkedin.com' not in url:
                result['website'] = url
                break

    return result


def extract_projects(text: str) -> list:
    """
    Detect if resume contains project descriptions.
    Returns list of project-related keywords and URLs found.
    """
    found = set()
    text_lower = text.lower()
    for pattern in PROJECT_PATTERNS:
        if pattern in text_lower:
            found.add(pattern)
    # Extract GitHub/GitLab repo names
    repo_urls = re.findall(r'(?:github|gitlab)\.com/[a-zA-Z0-9\-]+/[a-zA-Z0-9\-_.]+', text_lower)
    for url in repo_urls:
        found.add(url)
    return sorted(list(found))


def extract_industry(text: str) -> str:
    """Detect industry sector from resume text. Returns most likely industry or empty string."""
    text_lower = text.lower()
    counts = {}
    for pattern, industry in INDUSTRY_PATTERNS.items():
        if pattern in text_lower:
            counts[industry] = counts.get(industry, 0) + 1
    if counts:
        return max(counts, key=counts.get)
    return ''


def infer_fields_from_skills(skills: list) -> list:
    """
    Infer job fields based on extracted skills.
    Uses SKILL_TO_FIELD_MAP to map individual skills to broader fields.
    This provides a secondary field inference when direct field keywords are missing.
    """
    field_counts = {}
    for skill in skills:
        field = SKILL_TO_FIELD_MAP.get(skill)
        if field:
            field_counts[field] = field_counts.get(field, 0) + 1
    # Return fields sorted by frequency (most relevant first)
    return sorted(field_counts.keys(), key=lambda x: field_counts[x], reverse=True)


def classify_resume(text: str) -> dict:
    """
    Classify resume into a job category using enhanced rule-based approach.
    Now extracts: education, work history, projects, software/tools,
    experience level, contact info, companies, durations, industry.

    Returns: {
        category, confidence, skills, fields,
        education (dict), work_history (list), projects (list),
        software_tools (list), experience_level (str),
        contact_info (dict), companies (list), durations (list),
        industry (str)
    }
    """
    skills = extract_skills(text)
    fields = extract_fields(text)
    education = extract_education(text)
    work_history = extract_work_history(text)
    projects = extract_projects(text)
    software_tools = extract_software_tools(text)
    experience_level = extract_experience_level(text, skills, work_history)
    contact_info = extract_contact_info(text)
    companies = extract_companies(text)
    durations = extract_durations(text)
    industry = extract_industry(text)

    category = '\u0633\u0627\u06cc\u0631'
    confidence = 0.3

    # Primary: use detected fields
    if fields:
        field_counts = {}
        for f in fields:
            field_counts[f] = field_counts.get(f, 0) + 1
        category = max(field_counts, key=field_counts.get)
        confidence = min(0.95, 0.5 + len(skills) * 0.05)

    # Secondary: use skills to infer fields when no direct field found
    if category == '\u0633\u0627\u06cc\u0631' and skills:
        inferred_fields = infer_fields_from_skills(skills)
        if inferred_fields:
            category = inferred_fields[0]
            confidence = 0.65

    # Tertiary: use skill-set heuristics for category
    if category == '\u0633\u0627\u06cc\u0631' and skills:
        dev_skills = {'Python', 'JavaScript', 'Java', 'Django', 'React', 'Node.js',
                      'C#', 'C++', 'PHP', '.NET', 'TypeScript', 'Vue.js', 'Flutter',
                      'Go', 'Rust', 'Spring', 'Laravel', 'Ruby'}
        data_skills = {'Machine Learning', 'Deep Learning', 'NLP', 'Data Science',
                       'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn'}
        design_skills = {'Figma', 'Photoshop', 'Illustrator', 'UI/UX', 'Sketch', 'Adobe XD'}
        marketing_skills = {'SEO', 'Digital Marketing', 'Google Analytics',
                           'Content Marketing', 'Google Ads', 'SEMrush'}
        devops_skills = {'Docker', 'Kubernetes', 'AWS', 'Azure', 'CI/CD',
                        'Terraform', 'Ansible', 'Jenkins', 'Prometheus'}
        security_skills = {'Penetration Testing', 'OWASP', 'Burp Suite', 'Cisco',
                         'Mikrotik', 'Nmap', 'Wireshark', 'Metasploit'}
        mobile_skills = {'Flutter', 'React Native', 'Swift', 'Kotlin',
                        'Dart', 'Ionic', 'Xamarin'}

        skill_set = set(skills)
        category_scores = {
            'DevOps \u0648 \u0632\u06cc\u0631\u0633\u0627\u062e\u062a': len(skill_set & devops_skills),
            '\u0627\u0645\u0646\u06cc\u062a \u0633\u0627\u06cc\u0628\u0631\u06cc': len(skill_set & security_skills),
            '\u0628\u0631\u0646\u0627\u0645\u0647\u200c\u0646\u0648\u06cc\u0633 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631': len(skill_set & dev_skills),
            '\u0639\u0644\u0645 \u062f\u0627\u062f\u0647 \u0648 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc': len(skill_set & data_skills),
            '\u0637\u0631\u0627\u062d\u06cc \u06af\u0631\u0627\u0641\u06cc\u06a9 \u0648 UI/UX': len(skill_set & design_skills),
            '\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0648 \u0641\u0631\u0648\u0634': len(skill_set & marketing_skills),
        }
        best_cat = max(category_scores, key=category_scores.get)
        if category_scores[best_cat] > 0:
            category = best_cat
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

    # Boost if experience level is confidently detected
    if experience_level != 'unknown':
        confidence = min(0.95, confidence + 0.02)

    return {
        'category': category,
        'confidence': round(confidence, 3),
        'skills': skills,
        'fields': fields,
        'education': education,
        'work_history': work_history,
        'projects': projects,
        'software_tools': software_tools,
        'experience_level': experience_level,
        'contact_info': contact_info,
        'companies': companies,
        'durations': durations,
        'industry': industry,
    }


def suggest_search_keywords(text: str, skills: list, fields: list) -> str:
    """Generate optimal search keywords from resume analysis.

    Priority: field + strongest skills + work titles + education.
    Generates a keyword string optimized for job search platforms.
    """
    keywords = []
    if fields:
        keywords.append(fields[0])
    for skill in skills[:5]:
        if skill not in keywords:
            keywords.append(skill)
    return ' '.join(keywords[:6])

