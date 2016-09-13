from django import template

register = template.Library()

@register.simple_tag
def llegit(usuari, conversacio):
    return conversacio.tots_llegits(usuari)
