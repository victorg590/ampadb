from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()

@register.filter
def autourl(value):
    try:
        url = value.get_absolute_url()
    except AttributeError:
        return value
    return format_html('<a href={}>{}</a>', mark_safe(url), str(value))
