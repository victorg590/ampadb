from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter
def pytr(value):
    if value is True:
        ret = '<span style="color:green">Sí</span>'
    elif value is False:
        ret = '<span style="color:red">No</span>'
    elif value is None:
        ret = '-'
    else:
        return value
    return mark_safe(ret)
