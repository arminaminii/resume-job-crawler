"""
Skill-to-Platform Mapper Service

PURPOSE: When a user selects categories (or resume auto-detects them),
each platform needs DIFFERENT optimal search terms. This service generates
platform-specific keywords and parameters for maximum result relevance.

ARCHITECTURE:
1. JobCategory model has per-platform slug fields (jobvision_slug, estekhdam_slug, irantalent_slug)
2. SkillMapper takes selected categories + resume data → generates platform-specific queries
3. Each query uses the platform's native terminology for best results

EXAMPLE:
  Category: "Python Backend Developer"
  → Jobvision: keyword="python django" + categorySlugs=["python", "django-backend"]
  → IranTalent: keyword="python backend developer" + location_slugs
  → E-estekhdam: keyword="python" (API mostly ignores it anyway)

DESIGN DECISIONS:
- Platform slugs from DB take priority (they're curated for each site)
- Fallback: use category's keywords_en/keywords_fa joined
- Fallback 2: use skills joined
- For E-estekhdam: only send keywords (slug filtering doesn't work)
"""
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

# Farsi-to-English normalization map
# When a skill is detected, use these EXACT terms for each platform.
# Format: { 'skill_keyword': { 'platform_id': 'platform_specific_keyword' } }
SKILL_ALIASES = {
    # --- Programming Languages ---
    'python': {
        'jobvision': 'python',
        'irantalent': 'python',
        'e_estekhdam': 'python',
    },
    'javascript': {
        'jobvision': 'javascript',
        'irantalent': 'javascript',
        'e_estekhdam': 'javascript',
    },
    'typescript': {
        'jobvision': 'typescript',
        'irantalent': 'typescript',
        'e_estekhdam': 'typescript',
    },
    'java': {
        'jobvision': 'java',
        'irantalent': 'java',
        'e_estekhdam': 'java',
    },
    'c#': {
        'jobvision': 'سی شارپ',
        'irantalent': 'c#',
        'e_estekhdam': 'سی شارپ',
    },
    'php': {
        'jobvision': 'php',
        'irantalent': 'php',
        'e_estekhdam': 'php',
    },
    'go': {
        'jobvision': 'golang',
        'irantalent': 'go golang',
        'e_estekhdam': 'go',
    },
    'rust': {
        'jobvision': 'rust',
        'irantalent': 'rust',
        'e_estekhdam': 'rust',
    },
    'swift': {
        'jobvision': 'ios swift',
        'irantalent': 'ios swift',
        'e_estekhdam': 'swift',
    },
    'kotlin': {
        'jobvision': 'kotlin android',
        'irantalent': 'kotlin android',
        'e_estekhdam': 'kotlin',
    },
    # --- Frameworks ---
    'django': {
        'jobvision': 'django',
        'irantalent': 'django',
        'e_estekhdam': 'django',
    },
    'react': {
        'jobvision': 'react',
        'irantalent': 'react',
        'e_estekhdam': 'react',
    },
    'angular': {
        'jobvision': 'angular',
        'irantalent': 'angular',
        'e_estekhdam': 'angular',
    },
    'vue': {
        'jobvision': 'vue js',
        'irantalent': 'vue.js',
        'e_estekhdam': 'vue',
    },
    'next.js': {
        'jobvision': 'nextjs next.js',
        'irantalent': 'next.js',
        'e_estekhdam': 'nextjs',
    },
    'node.js': {
        'jobvision': 'nodejs node.js',
        'irantalent': 'node.js',
        'e_estekhdam': 'nodejs',
    },
    'flask': {
        'jobvision': 'flask',
        'irantalent': 'flask',
        'e_estekhdam': 'flask',
    },
    'laravel': {
        'jobvision': 'laravel',
        'irantalent': 'laravel',
        'e_estekhdam': 'laravel',
    },
    '.net': {
        'jobvision': '.net',
        'irantalent': '.net',
        'e_estekhdam': '.net',
    },
    # --- DevOps / Infra ---
    'docker': {
        'jobvision': 'docker',
        'irantalent': 'docker',
        'e_estekhdam': 'docker',
    },
    'kubernetes': {
        'jobvision': 'kubernetes k8s',
        'irantalent': 'kubernetes',
        'e_estekhdam': 'kubernetes',
    },
    'aws': {
        'jobvision': 'aws',
        'irantalent': 'aws',
        'e_estekhdam': 'aws',
    },
    'devops': {
        'jobvision': 'devops',
        'irantalent': 'devops',
        'e_estekhdam': 'devops',
    },
    'ci/cd': {
        'jobvision': 'ci cd',
        'irantalent': 'ci/cd',
        'e_estekhdam': 'ci cd',
    },
    'linux': {
        'jobvision': 'linux',
        'irantalent': 'linux',
        'e_estekhdam': 'linux',
    },
    # --- Data / AI ---
    'machine learning': {
        'jobvision': 'machine learning',
        'irantalent': 'machine learning',
        'e_estekhdam': 'machine learning',
    },
    'deep learning': {
        'jobvision': 'deep learning',
        'irantalent': 'deep learning',
        'e_estekhdam': 'deep learning',
    },
    'data science': {
        'jobvision': 'data science',
        'irantalent': 'data science',
        'e_estekhdam': 'data science',
    },
    'nlp': {
        'jobvision': 'nlp پردازش زبان طبیعی',
        'irantalent': 'nlp',
        'e_estekhdam': 'nlp',
    },
    'tensorflow': {
        'jobvision': 'tensorflow',
        'irantalent': 'tensorflow',
        'e_estekhdam': 'tensorflow',
    },
    'pytorch': {
        'jobvision': 'pytorch',
        'irantalent': 'pytorch',
        'e_estekhdam': 'pytorch',
    },
    # --- Design ---
    'ui/ux': {
        'jobvision': 'ui ux',
        'irantalent': 'ui ux',
        'e_estekhdam': 'طراحی رابط کاربری',
    },
    'figma': {
        'jobvision': 'figma',
        'irantalent': 'figma',
        'e_estekhdam': 'figma',
    },
    'graphic design': {
        'jobvision': 'طراحی گرافیک',
        'irantalent': 'graphic design',
        'e_estekhdam': 'طراحی گرافیک',
    },
    # --- Marketing ---
    'seo': {
        'jobvision': 'سئو seo',
        'irantalent': 'seo',
        'e_estekhdam': 'سئو',
    },
    'digital marketing': {
        'jobvision': 'دیجیتال مارکتینگ',
        'irantalent': 'digital marketing',
        'e_estekhdam': 'دیجیتال مارکتینگ',
    },
    'content marketing': {
        'jobvision': 'تولید محتوا',
        'irantalent': 'content marketing',
        'e_estekhdam': 'تولید محتوا',
    },
    # --- Mobile ---
    'android': {
        'jobvision': 'android',
        'irantalent': 'android',
        'e_estekhdam': 'android',
    },
    'ios': {
        'jobvision': 'ios',
        'irantalent': 'ios',
        'e_estekhdam': 'ios',
    },
    'flutter': {
        'jobvision': 'flutter',
        'irantalent': 'flutter',
        'e_estekhdam': 'flutter',
    },
    'react native': {
        'jobvision': 'react native',
        'irantalent': 'react native',
        'e_estekhdam': 'react native',
    },
    # --- Management ---
    'product manager': {
        'jobvision': 'product manager',
        'irantalent': 'product manager',
        'e_estekhdam': 'مدیر محصول',
    },
    'project manager': {
        'jobvision': 'project manager',
        'irantalent': 'project manager',
        'e_estekhdam': 'مدیر پروژه',
    },
    'scrum master': {
        'jobvision': 'scrum',
        'irantalent': 'scrum master',
        'e_estekhdam': 'scrum',
    },
    # --- QA ---
    'qa': {
        'jobvision': 'qa تست',
        'irantalent': 'qa',
        'e_estekhdam': 'qa',
    },
    'selenium': {
        'jobvision': 'selenium',
        'irantalent': 'selenium',
        'e_estekhdam': 'selenium',
    },
    # --- Database ---
    'sql': {
        'jobvision': 'sql',
        'irantalent': 'sql',
        'e_estekhdam': 'sql',
    },
    'mongodb': {
        'jobvision': 'mongodb',
        'irantalent': 'mongodb',
        'e_estekhdam': 'mongodb',
    },
    'postgresql': {
        'jobvision': 'postgresql',
        'irantalent': 'postgresql',
        'e_estekhdam': 'postgresql',
    },
    # --- Security ---
    'cybersecurity': {
        'jobvision': 'امنیت سایبری',
        'irantalent': 'cybersecurity',
        'e_estekhdam': 'امنیت سایبری',
    },
    'penetration testing': {
        'jobvision': 'تست نفوذ',
        'irantalent': 'penetration testing',
        'e_estekhdam': 'تست نفوذ',
    },
    # --- Network ---
    'network': {
        'jobvision': 'شبکه',
        'irantalent': 'network',
        'e_estekhdam': 'شبکه',
    },
    # --- Accounting/Finance ---
    'accounting': {
        'jobvision': 'حسابداری',
        'irantalent': 'accounting',
        'e_estekhdam': 'حسابداری',
    },
}

# Farsi-to-English normalization map
FA_EN_MAP = {
    'پایتون': 'python', 'جنگو': 'django', 'ریکت': 'react', 'جاوا اسکریپت': 'javascript',
    'لاراول': 'laravel', 'فلاتر': 'flutter', 'سی شارپ': 'c#', 'داکر': 'docker',
    'سئو': 'seo', 'فیکسما': 'figma', 'لینوکس': 'linux', 'اندروید': 'android',
    'دیجیتال مارکتینگ': 'digital marketing', 'تولید محتوا': 'content marketing',
    'امنیت سایبری': 'cybersecurity', 'شبکه': 'network', 'حسابداری': 'accounting',
    'مدیر محصول': 'product manager', 'مدیر پروژه': 'project manager',
    'طراحی گرافیک': 'graphic design', 'طراحی رابط کاربری': 'ui/ux',
}


class SkillMapper:
    """
    Generates platform-specific search parameters from selected categories.
    
    Usage:
        mapper = SkillMapper.from_categories(selected_slugs, custom_keywords, resume)
        
        # Get platform-specific queries
        jv_query = mapper.get_query('jobvision')   # {'keywords': 'python django', 'category_slugs': [...]}
        it_query = mapper.get_query('irantalent')   # {'keywords': 'python backend developer'}
        ee_query = mapper.get_query('e_estekhdam') # {'keywords': 'python'}
    """

    def __init__(self):
        self._all_skills = []           # Raw skills from all categories
        self._all_positions = []       # Raw positions from all categories
        self._all_keywords_en = []     # English keywords
        self._all_keywords_fa = []     # Persian keywords
        self._custom_keywords = ''     # User's custom input
        self._category_slugs = {}      # {platform: [slug1, slug2]}
        self._platform_keywords = {}   # {platform: 'optimal search string'}

    @classmethod
    def from_search(cls, selected_slugs: list, custom_keywords: str = '',
                   resume_skills: list = None, resume_text: str = '') -> 'SkillMapper':
        """
        Build mapper from search context.
        
        Args:
            selected_slugs: Category slugs selected by user
            custom_keywords: User's manual keyword input
            resume_skills: Skills extracted from resume (list of strings)
            resume_text: Full resume text
        """
        mapper = cls()

        from core.models import JobCategory
        categories = JobCategory.objects.filter(
            slug__in=selected_slugs, is_active=True
        ).select_related('parent')

        mapper._custom_keywords = custom_keywords or ''

        # Collect all skills, positions, keywords from selected categories
        for cat in categories:
            mapper._all_skills.extend(cat.skills or [])
            mapper._all_positions.extend(cat.positions or [])
            mapper._all_keywords_en.extend(cat.keywords_en or [])
            mapper._all_keywords_fa.extend(cat.keywords_fa or [])

            # Collect platform-specific slugs
            for platform, field in [('jobvision', 'jobvision_slug'),
                                     ('e_estekhdam', 'estekhdam_slug'),
                                     ('irantalent', 'irantalent_slug')]:
                slug = getattr(cat, field, '')
                if slug:
                    mapper._category_slugs.setdefault(platform, [])
                    mapper._category_slugs[platform].append(slug)

        # Deduplicate
        mapper._all_skills = list(OrderedDict.fromkeys(mapper._all_skills))
        mapper._all_positions = list(OrderedDict.fromkeys(mapper._all_positions))
        mapper._all_keywords_en = list(OrderedDict.fromkeys(mapper._all_keywords_en))
        mapper._all_keywords_fa = list(OrderedDict.fromkeys(mapper._all_keywords_fa))

        # Also add resume skills if provided
        if resume_skills:
            for s in resume_skills:
                if s not in mapper._all_skills:
                    mapper._all_skills.append(s)

        # Generate platform-specific keywords
        mapper._generate_platform_keywords()

        return mapper

    def _normalize_skill(self, skill: str) -> str:
        """Normalize a skill to lowercase for lookup."""
        s = skill.strip().lower()
        # Try Farsi → English normalization
        if s in FA_EN_MAP:
            return FA_EN_MAP[s]
        return s

    def _get_platform_alias(self, skill: str, platform: str) -> str:
        """Get platform-specific search term for a skill."""
        normalized = self._normalize_skill(skill)
        # Check direct alias
        if normalized in SKILL_ALIASES:
            aliases = SKILL_ALIASES[normalized]
            return aliases.get(platform, normalized)
        # No alias — return normalized
        return normalized

    def _generate_platform_keywords(self):
        """Generate optimal search keywords for each platform.
        
        KEY RESEARCH FINDING (2026-07-22):
        - JobVision API IGNORES categorySlugs. Only 'keyword' works.
        - IranTalent API IGNORES slug. Only 'keyword' works.
        - E-estekhdam API is BROKEN (ignores all params).
        
        Strategy for ALL platforms: use top 2-3 skills as keyword.
        Custom keywords always take priority.
        """
        # Priority order: custom keywords > skills > positions > keywords_en
        all_terms = self._all_skills + self._all_positions + self._all_keywords_en
        unique_terms = list(OrderedDict.fromkeys(all_terms))

        for platform in ['jobvision', 'irantalent', 'e_estekhdam']:
            # ALL platforms: same strategy — top skills as keyword
            if self._custom_keywords:
                kw = self._custom_keywords.strip()[:50]
            else:
                # Use top 2-3 most relevant skills
                mapped = []
                for term in unique_terms[:8]:
                    alias = self._get_platform_alias(term, platform)
                    if alias and alias not in mapped:
                        mapped.append(alias)
                    if len(mapped) >= 3:
                        break
                kw = ' '.join(mapped)
            
            # Deduplicate words within keyword
            all_words = kw.split()
            seen = set()
            deduped = []
            for w in all_words:
                w_lower = w.lower()
                if w_lower not in seen:
                    seen.add(w_lower)
                    deduped.append(w)
            self._platform_keywords[platform] = ' '.join(deduped[:5])

        logger.info(f"SkillMapper generated keywords:")
        for p, kw in self._platform_keywords.items():
            slugs = self._category_slugs.get(p, [])
            logger.info(f"  {p}: keywords='{kw[:60]}', slugs={slugs[:3]}")

    def get_query(self, platform: str) -> dict:
        """
        Get complete query parameters for a specific platform.
        
        Returns dict with:
            - keywords: str (platform-specific search terms)
            - category_slugs: list (platform-specific category slugs)
        """
        return {
            'keywords': self._platform_keywords.get(platform, ''),
            'category_slugs': self._category_slugs.get(platform, []),
        }

    def get_debug_info(self) -> dict:
        """Return debug info about the mapping."""
        return {
            'total_skills': len(self._all_skills),
            'total_positions': len(self._all_positions),
            'total_keywords_en': len(self._all_keywords_en),
            'total_keywords_fa': len(self._all_keywords_fa),
            'custom_keywords': self._custom_keywords,
            'platform_keywords': dict(self._platform_keywords),
            'platform_slugs': dict(self._category_slugs),
        }