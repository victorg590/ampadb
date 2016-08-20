from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.simple_tag
def pyprint(value=None):
    '''Imprimeix dades desde un 'template'. Útil per a depuració.'''
    print(value)
