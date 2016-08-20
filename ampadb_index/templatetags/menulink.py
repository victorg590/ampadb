from django import template
from django.utils.html import format_html, mark_safe
from django.urls import reverse

register = template.Library()

@register.simple_tag
def menulink(text, href, *args, **kwargs):
    url = reverse(href, args=args, kwargs=kwargs)
    return format_html('<a href="{}">{}</a>',
        url, mark_safe(text))
