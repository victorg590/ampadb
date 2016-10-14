from django import template
from django.utils.html import format_html
from usermanager.models import Profile

register = template.Library()


@register.filter
def printuser(value):
    val = "{nom} {cognoms}".format(nom=(value.first_name or ''),
                                   cognoms=(value.last_name or '')).strip()
    if val:
        return val
    try:
        profile = Profile.objects.get(user=value)
        return str(profile.alumne)
    except Profile.DoesNotExist:
        return format_html('<span class="username">{}</span>', str(value))
