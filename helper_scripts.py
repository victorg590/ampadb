"""Scripts que faciliten l'administració de la base de dades

S'han d'executar amb
    `$ python manage.py shell`
    '>>> from . import helper_scripts'
"""

from contactboard.models import Curs, Classe
from django.db import transaction

CURSOS = [('1ESO', '1er ESO', 1), ('2ESO', '2on ESO', 2),
          ('3ESO', '3er ESO', 3), ('4ESO', '4rt ESO', 4),
          ('1BTX', '1er Batxillerat', 5), ('2BTX', '2on Batxillerat', 6)]


def gencurs():
    """Crea els cursos 1er ESO A - 2on Batx E"""
    creats = []
    with transaction.atomic():
        for curs in CURSOS:
            curs_obj = Curs.objects.get_or_create(
                id_interna=curs[0],
                defaults={
                    'nom': curs[1],
                    'ordre': curs[2]
                })[0]
            for classe in ('A', 'B', 'C', 'D', 'E'):
                creats.append(
                    Classe.objects.update_or_create(
                        id_interna=(curs_obj.id_interna + classe),
                        defaults={
                            'nom': classe,
                            'curs': curs
                        }))
    return creats
