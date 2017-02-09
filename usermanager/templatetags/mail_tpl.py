from django import template
from django.utils.html import mark_safe
from ampadb_index.parse_md import clean
from string import Template
from ..models import Profile

register = template.Library()


@register.simple_tag
def mail_template(template, uu, server_url):
    tpl = Template(template)
    alumne = Profile.objects.get(unregisteredUser=uu).alumne
    variables = {
        'nom': clean(alumne.nom),
        'cognoms': clean(alumne.cognoms),
        'classe': clean(alumne.classe.nom),
        'usuari': uu.username,
        'codi': uu.codi,
        'url': server_url
    }
    return mark_safe(tpl.safe_substitute(variables))
