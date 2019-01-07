import csv
import json
from collections import namedtuple
from io import TextIOWrapper
import chardet
from django.db import transaction
from django.db.models import OuterRef, Subquery
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


def _parse_ies_csv(input_csv, importacio):
    # input_csv ha de ser un stream de text
    try:
        reader = csv.DictReader(input_csv, dialect=IesDialect)
    except csv.Error:
        input_csv.seek(0)
        reader = csv.DictReader(input_csv, dialect='excel')
    classes = set()
    new_data = []
    try:
        for row in reader:
            nom = row['NOM'] or ''
            nom = nom.strip()
            if not nom:
                raise InvalidFormat.falta_a_fila('NOM', row.values())

            cognom1 = row['COGNOM 1'] or ''
            cognom1 = cognom1.strip()
            if not cognom1:
                raise InvalidFormat.falta_a_fila('COGNOM 1', row.values())

            cognom2 = row['COGNOM 2'] or ''
            cognom2 = cognom2.strip()
            if cognom2:
                cognoms = '{} {}'.format(cognom1, cognom2)
            else:
                cognoms = cognom1

            classe = row['CLASSE'] or ''
            classe = classe.strip()
            if not classe:
                raise InvalidFormat.falta_a_fila('CLASSE', row.values())

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
    ImportData.objects.filter(
        importacio=importacio,
        alumne__isnull=True).update(alumne=Subquery(
            Alumne.objects.filter(
                nom=OuterRef('nom'), cognoms=OuterRef('cognoms')).order_by()
            .values('pk')))
    ClassMap.objects.bulk_create([
        ClassMap(importacio=importacio, codi_classe=c, classe_mapejada=None)
        for c in classes
    ])


def parse_ies_csv(input_csv_bin, importacio):
    try:
        try:
            input_csv = TextIOWrapper(input_csv_bin, encoding='utf8')
            return _parse_ies_csv(input_csv, importacio)
        except UnicodeDecodeError:
            encoding_guess = chardet.detect(input_csv_bin.read(1024))
            if encoding_guess['confidence'] < 0.90:
                raise InvalidFormat(
                    "No es reconeix el format de text (s'esperava UTF-8)")
            input_csv_bin.seek(0)
            input_csv = TextIOWrapper(
                input_csv_bin, encoding=encoding_guess['encoding'])
            return _parse_ies_csv(input_csv, importacio)
    except csv.Error:
        raise InvalidFormat('No és un arxiu CSV correcte (error de sintaxi)')


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

    classes_buides = set(assoc_classes.values())

    import_alumnes = ImportData.objects.filter(
        importacio=imp).defer('importacio')
    # Nous alumnes
    for ialumne in import_alumnes.filter(alumne=None):
        canvis_nous.append(
            AddAlumne(
                importacio=imp,
                dada_relacionada=ialumne,
                nova_classe=assoc_classes[ialumne.codi_classe]))
        classes_buides -= {assoc_classes[ialumne.codi_classe]}

    # Alumnes moguts
    for ialumne in import_alumnes.filter(
            alumne__isnull=False).select_related('alumne', 'alumne__classe').only(
                'alumne__classe', 'alumne', 'pk', 'codi_classe'):
        if ialumne.alumne.classe.pk != assoc_classes[ialumne.codi_classe]:
            canvis_moguts.append(
                MoveAlumne(
                    importacio=imp,
                    dada_relacionada=ialumne,
                    nova_classe=assoc_classes[ialumne.codi_classe],
                    alumne=ialumne.alumne))
        classes_buides -= {assoc_classes[ialumne.codi_classe]}

    # Alumnes eliminats
    for dalumne in Alumne.objects.exclude(pk__in=import_alumnes.exclude(
            alumne=None).values('alumne')).only('pk').order_by():
        canvis_eliminats.append(DeleteAlumne(importacio=imp, alumne=dalumne))

    AddAlumne.objects.bulk_create(canvis_nous)
    MoveAlumne.objects.bulk_create(canvis_moguts)
    DeleteAlumne.objects.bulk_create(canvis_eliminats)
    classes_buides = Classe.objects.filter(
        pk__in=classes_buides).only('pk').order_by()
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
        for a in AddAlumne.objects.filter(
            importacio=imp).select_related('dada_relacionada', 'nova_classe')
    ])
    # Moure alumnes existents
    # Nota per a futures optimitzacions: és la operació més costosa, però
    # Django no permet cap forma fàcil d'optimitzar-la (s'hauria d'utilitzar
    # SQL directament)
    for move_op in MoveAlumne.objects.filter(importacio=imp).select_related(
            'alumne', 'nova_classe'):
        # Així evita enviar signals (innecessàries en aquest cas)
        Alumne.objects.filter(pk=move_op.alumne.pk).update(
            classe=move_op.nova_classe)
    # Eliminar alumnes antics
    Alumne.objects.filter(
        pk__in=DeleteAlumne.objects.filter(importacio=imp).values('alumne')).delete()
    Classe.objects.filter(
        pk__in=DeleteClasse.objects.filter(importacio=imp).values('classe')).delete()
    imp.delete()
