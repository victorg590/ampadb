from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def printuser(value):
    val = "{nom} {cognoms}".format(nom=(value.first_name or ''),
        cognoms=(value.last_name or '')).strip()
    if not val:
        return format_html('<span class="username">{}</span>', str(value))
    return val
