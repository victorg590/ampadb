"""Scripts que faciliten l'administració de la base de dades

S'han d'executar amb
    `$ python manage.py shell`
    '>>> from . import helper_scripts'
"""

from contactboard.models import Curs, Classe, Alumne
from django.db import transaction

cursos = [
    ('1ESO', '1er ESO', 1),
    ('2ESO', '2on ESO', 2),
    ('3ESO', '3er ESO', 3),
    ('4ESO', '4rt ESO', 4),
    ('1BTX', '1er Batxillerat', 5),
    ('2BTX', '2on Batxillerat', 6)
]


def gencurs():
    """Crea els cursos 1er ESO A - 2on Batx E"""
    creats = []
    with transaction.atomic():
        for c in cursos:
            curs = Curs.objects.get_or_create(
                id_interna=c[0],
                defaults={'nom': c[1], 'ordre': c[2]}
            )[0]
            for classe in ('A', 'B', 'C', 'D', 'E'):
                creats.append(Classe.objects.update_or_create(
                    id_interna=(curs.id_interna + classe),
                    defaults={'nom': classe, 'curs': curs})
                )
    return creats

def updateAll():
    """Desa tots els models que han canviat des de la versió 1.0.

    Aixó permet emitir les senyals associades al model.
    """
    # Alumnes: correu_alumne = user.email, nom_alumne = user.name...
    for a in Alumne.objects.all():
        a.save()
