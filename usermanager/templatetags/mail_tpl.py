from string import Template
from django import template
from django.utils.html import mark_safe
from ampadb_index.parse_md import clean
from ..models import Profile

register = template.Library()


@register.simple_tag
def mail_template(tpl, uuser, server_url):
    tpl = Template(tpl)
    alumne = Profile.objects.get(unregisteredUser=uuser).alumne
    variables = {
        'nom': clean(alumne.nom),
        'cognoms': clean(alumne.cognoms),
        'classe': clean(alumne.classe.nom),
        'usuari': uuser.username,
        'codi': uuser.codi,
        'url': server_url
    }
    return mark_safe(tpl.safe_substitute(variables))
