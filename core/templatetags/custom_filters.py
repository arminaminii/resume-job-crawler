from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Template filter: {{ mydict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, key)
    return key


@register.filter
def split_path(value):
    """Split career_path string by ' > ' (arrow separator)."""
    if not value:
        return []
    return value.split(' > ')


# Precompiled pattern to strip dangerous SVG attributes/elements
_SVG_DANGEROUS_RE = re.compile(
    r'<\s*/?\s*(script|iframe|object|embed|link|meta|base|import|use[^>]*href)[^>]*>|'
    r'\bon\w+\s*=|'
    r'javascript\s*:|'
    r'data\s*:\s*text/html',
    re.IGNORECASE,
)


@register.filter
def sanitize_svg(value):
    """Strip dangerous elements/attributes from SVG markup.

    Use instead of |safe on user-editable SVG fields (e.g. icon_svg).
    Still returns a SafeString so the browser renders the SVG.
    """
    if not value:
        return ''
    cleaned = _SVG_DANGEROUS_RE.sub('', value)
    return mark_safe(cleaned)