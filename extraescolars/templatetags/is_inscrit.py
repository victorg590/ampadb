from django import template
from extraescolars.models import Inscripcio

register = template.Library()

@register.simple_tag
def is_inscrit(alumne, extraescolar):
    return Inscripcio.objects.filter(alumne=alumne,
        activitat=extraescolar).exists()
