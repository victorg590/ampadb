import csv
import json
from collections import namedtuple
from io import TextIOWrapper
import chardet
from django.db import transaction
from ampadb.support import gen_username, gen_codi
from contactboard.models import Classe, Alumne
from usermanager.models import Profile, UnregisteredUser
from .import_fmts import InvalidFormat, bytestream_to_text
from .models import ImportData, ClassMap, IesImport, AddAlumne, MoveAlumne, DeleteAlumne, DeleteClasse

ImportedAlumne = namedtuple('ImportedAlumne', ['nom', 'cognoms', 'classe'])


class IesDialect(csv.Dialect):  # pylint: disable=too-few-public-methods
    delimiter = ','
    doublequote = False
    escapechar = '\\'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def parse_ies_csv(input_csv_bin, importacio):
    try:
        input_csv = TextIOWrapper(input_csv_bin, encoding='utf8')
    except UnicodeDecodeError:
        encoding_guess = chardet.detect(input_csv_bin.read(1024))
        if encoding_guess['confidence'] < 0.90:
            raise
        input_csv_bin.seek(0)
        input_csv = TextIOWrapper(
            input_csv_bin, encoding=encoding_guess['encoding'])
    input_csv.seek(0)
    try:
        reader = csv.DictReader(input_csv, dialect=IesDialect)
    except csv.Error:
        input_csv.seek(0)
        reader = csv.DictReader(input_csv, dialect='excel')
    classes = set()
    new_data = []
    try:
        for row in reader:
            nom = row['NOM'].strip()
            if not nom:
                raise InvalidFormat.falta_a_fila('NOM', row)

            cognom1 = row['COGNOM 1'].strip()
            if not cognom1:
                raise InvalidFormat.falta_a_fila('COGNOM 1', row)

            cognom2 = row['COGNOM 2'].strip()
            if cognom2:
                cognoms = '{} {}'.format(cognom1, cognom2)
            else:
                cognoms = cognom1

            classe = row['CLASSE'].strip()
            if not classe:
                raise InvalidFormat.falta_a_fila('CLASSE', row)

            new_data.append(
                ImportData(
                    importacio=importacio,
                    nom=nom,
                    cognoms=cognoms,
                    codi_classe=classe))
            classes |= {classe}
    except KeyError as ex:
        raise InvalidFormat.falta_columna(ex)

    ImportData.objects.bulk_create(new_data)
    ClassMap.objects.bulk_create([
        ClassMap(
            importacio=importacio, codi_classe=c, classe_mapejada=None)
        for c in classes
    ])


def invalidar_canvis(imp):
    imp.canvis_addalumne.all().delete()
    imp.canvis_movealumne.all().delete()
    imp.canvis_deletealumne.all().delete()
    imp.canvis_deleteclasse.all().delete()
    imp.canvis_calculats = False

def invalidar_canvis_tots():
    with transaction.atomic():
        AddAlumne.objects.all().delete()
        MoveAlumne.objects.all().delete()
        DeleteAlumne.objects.all().delete()
        DeleteClasse.objects.all().delete()
        IesImport.objects.update(canvis_calculats=False)


def calcular_canvis(imp):
    if imp.canvis_calculats:
        return
    canvis_nous = []
    canvis_moguts = []
    canvis_eliminats = []
    assoc_classes = {}
    for mapa in ClassMap.objects.filter(
            importacio=imp,
            classe_mapejada__isnull=False).select_related('classe_mapejada'):
        assoc_classes[mapa.codi_classe] = mapa.classe_mapejada
    alumnes_existents = Alumne.objects.only('pk', 'nom', 'cognoms',
                                            'classe').select_related('classe').order_by(
                                                'nom', 'cognoms').iterator()
    alumnes_nous = ImportData.objects.filter(importacio=imp).order_by(
        'nom', 'cognoms').iterator()
    classes_no_buides = set()
    ae = next(alumnes_existents, None)
    an = next(alumnes_nous, None)
    while ae is not None and an is not None:
        if (ae.nom, ae.cognoms) < (an.nom, an.cognoms):
            # Alumne ae ha sigut eliminat
            canvis_eliminats.append(
                DeleteAlumne(
                    importacio=imp, alumne=ae, antiga_classe=ae.classe))
            ae = next(alumnes_existents, None)
        elif (ae.nom, ae.cognoms) > (an.nom, an.cognoms):
            # Alumne an és nou
            canvis_nous.append(
                AddAlumne(
                    importacio=imp,
                    dada_relacionada=an,
                    nova_classe=assoc_classes[an.codi_classe]))
            classes_no_buides |= {assoc_classes[an.codi_classe].pk}
            an = next(alumnes_nous, None)
        else:
            # Alumne ae = an existia. Comprovar si s'ha canviat de classe
            nova_classe = assoc_classes[an.codi_classe]
            if ae.classe != nova_classe:
                canvis_moguts.append(
                    MoveAlumne(
                        importacio=imp,
                        dada_relacionada=an,
                        antiga_classe=ae.classe,
                        nova_classe=nova_classe,
                        alumne=ae))
            classes_no_buides |= {nova_classe.pk}
            ae = next(alumnes_existents, None)
            an = next(alumnes_nous, None)
    while ae is not None:
        # La resta d'alumnes han sigut eliminats
        canvis_eliminats.append(
            DeleteAlumne(importacio=imp, alumne=ae, antiga_classe=ae.classe))
        ae = next(alumnes_existents, None)
    while an is not None:
        # La resta d'alumnes són nous
        canvis_nous.append(
            AddAlumne(
                importacio=imp,
                dada_relacionada=an,
                nova_classe=assoc_classes[an.codi_classe]))
        classes_no_buides |= {assoc_classes[an.codi_classe].pk}
        an = next(alumnes_nous, None)

    AddAlumne.objects.bulk_create(canvis_nous)
    MoveAlumne.objects.bulk_create(canvis_moguts)
    DeleteAlumne.objects.bulk_create(canvis_eliminats)
    classes_buides = Classe.objects.exclude(
        pk__in=classes_no_buides).only('pk').order_by()
    if imp.eliminar_classes_buides:
        DeleteClasse.objects.bulk_create(
            [DeleteClasse(importacio=imp, classe=c) for c in classes_buides])
    imp.canvis_calculats = True


def aplicar_canvis(imp):
    # Crear alumnes nous
    Alumne.objects.bulk_create([
        Alumne(
            nom=a.dada_relacionada.nom,
            cognoms=a.dada_relacionada.cognoms,
            classe=a.nova_classe)
        for a in AddAlumne.objects.filter(importacio=imp).select_related('dada_relacionada', 'nova_classe')
    ])
    # Moure alumnes existents
    # Nota per a futures optimitzacions: és la operació més costosa, però
    # Django no permet cap forma fàcil d'optimitzar-la (s'hauria d'utilitzar
    # SQL directament)
    for move_op in MoveAlumne.objects.filter(importacio=imp).select_related('alumne', 'nova_classe'):
        # Així evita enviar signals (innecessàries en aquest cas)
        Alumne.objects.filter(pk=move_op.alumne.pk).update(classe=move_op.nova_classe)
    # Eliminar alumnes antics
    Alumne.objects.filter(pk__in=DeleteAlumne.objects.filter(importacio=imp)).delete()
    Classe.objects.filter(pk__in=DeleteClasse.objects.filter(importacio=imp)).delete()
    invalidar_canvis(imp)