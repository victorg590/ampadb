from django import template

register = template.Library()

@register.simple_tag
def pyprint(value=None):
    '''Imprimeix dades desde un 'template'. Útil per a depuració.'''
    print(value)
