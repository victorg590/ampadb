from django import template
from missatges.models import Conversacio, EstatMissatge

register = template.Library()

@register.simple_tag
def llegit(usuari, conversacio):
    return conversacio.tots_llegits(usuari)
