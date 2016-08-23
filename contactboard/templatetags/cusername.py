from django import template
from django.contrib.auth.models import User
from django.utils.html import mark_safe, format_html

register = template.Library()

@register.filter
def cuser(value):
    if isinstance(value, User):
        return format_html('<span class="username">{}</span>', str(value))
    return format_html('{}', str(value))
