from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    """Safe dict getter for templates: {{ mydict|dict_get:key }}"""
    if not d:
        return None
    return d.get(key)
