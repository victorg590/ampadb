from django import template
from django.utils.html import mark_safe, format_html

register = template.Library()

@register.filter
def pytr(value):
    if value:
        ret = '<span style="color:green">Sí</span>'
    elif value is None:
        ret = '-'
    else:
        ret = '<span style="color:red">No</span>'
    return mark_safe(ret)

@register.filter
def pytricon(value):
    if value:
        color = '#008000'
        ret = 'ok'
    elif value is None:
        color = 'black'
        ret = 'minus'
    else:
        ret = 'remove'
        color = '#FF0000'
    return format_html(
        '<span class="glyphicon glyphicon-{}" style="color:{}"></span>',
        ret, color)
