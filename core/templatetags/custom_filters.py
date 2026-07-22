from django import template

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