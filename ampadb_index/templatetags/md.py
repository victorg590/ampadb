from django import template
from django.utils.html import mark_safe
import bleach
import markdown

register = template.Library()

@register.filter
def md(text):
    html = markdown.markdown(bleach.clean(text), output_format='html5',
        enable_attributes=False, lazy_ol=False,
        extensions=['markdown.extensions.extra'])
    return mark_safe(html)
