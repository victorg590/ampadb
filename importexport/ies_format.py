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
from .models import ImportData, ClassMap

ImportedAlumne = namedtuple('ImportedAlumne', ['nom', 'cognoms', 'classe'])


def parse_ies_csv(input_csv_bin, importacio):
    try:
        input_csv = TextIOWrapper(input_csv_bin, encoding='utf8')
    except UnicodeDecodeError:
        encoding_guess = chardet.detect(input_csv_bin.read(1024))
        if encoding_guess['confidence'] < 0.90:
            raise
        input_csv_bin.seek(0)
        input_csv = TextIOWrapper(input_csv_bin,
            encoding=encoding_guess['encoding'])
    dialect = csv.Sniffer().sniff(input_csv.read(1024), delimiters=',;')
    input_csv.seek(0)
    reader = csv.DictReader(input_csv, dialect=dialect)
    with transaction.atomic():
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
                
                ImportData.objects.create(
                    importacio=importacio,
                    nom=nom,
                    cognoms=cognoms,
                    codi_classe=classe
                )
        except KeyError as ex:
            raise InvalidFormat.falta_columna(ex)
        
        classes = ImportData.objects.values_list('codi_classe', flat=True)
        ClassMap.objects.bulk_create([ClassMap(importacio=importacio, 
            codi_classe=c, classe_mapejada=None) for c in classes])


def validate_row(row):
    try:
        nom = row['NOM'].strip()
    except KeyError as ex:
        raise InvalidFormat.falta_columna('NOM') from ex
    if not nom:
        raise InvalidFormat.falta_a_fila('NOM', row)

    try:
        cognom1 = row['COGNOM 1'].strip()
    except KeyError as ex:
        raise InvalidFormat.falta_columna('COGNOM 1') from ex
    if not cognom1:
        raise InvalidFormat.falta_a_fila('COGNOM 1', row)

    # COGNOM 2 opcional

    try:
        classe = row['CLASSE'].strip()
    except KeyError as ex:
        raise InvalidFormat.falta_columna('CLASSE') from ex
    if not classe:
        raise InvalidFormat.falta_a_fila('CLASSE', row)


def validate(inp):
    try:
        reader = csv.DictReader(bytestream_to_text(inp))
    except UnicodeDecodeError as ex:
        raise InvalidFormat('No és un arxiu de text (UTF-8)') from ex
    res = []
    for row in reader:
        validate_row(row)
        res.append(row)
    return res


def parse_row(row):
    nom = row['NOM'].strip()
    assert nom

    cognom1 = row['COGNOM 1'].strip()
    assert cognom1

    try:
        cognom2 = row['COGNOM 2'].strip()
    except KeyError:
        cognom2 = ''

    if cognom2:
        cognoms = cognom1 + ' ' + cognom2
    else:
        cognoms = cognom1
    assert cognoms

    classe = row['CLASSE'].strip()
    assert classe

    return ImportedAlumne(nom, cognoms, classe)


def parse(validated_inp):
    res = []
    for row in validated_inp:
        res.append(parse_row(row))
    return res


def unique_classes(parsed_inp):
    current = set()
    for alumne in parsed_inp:
        current |= {alumne.classe}
    return current


def val_json(inp, dicc):
    current = set()
    expected = unique_classes(parse(validate(inp)))
    for classe in dicc:
        if not Classe.objects.filter(id_interna=classe).exists():
            raise InvalidFormat('No existeix la classe "{}"'.format(classe))
        if dicc[classe] is None:
            continue
        for imp_classe in dicc[classe]:
            if imp_classe in current:
                raise InvalidFormat('Classe repetida: "{}"'.format(imp_classe))
            if imp_classe not in expected:
                raise InvalidFormat(
                    'Classe no esperada: "{}"'.format(imp_classe))
            current |= {imp_classe}
    if current < expected:
        raise InvalidFormat('Falten classes: {}'.format(expected - current))
    assert current == expected


def rev_json(in_dicc):
    if in_dicc is None:
        return json.dumps(None)
    out_dicc = {}
    for classe in in_dicc:
        if in_dicc[classe] is None:
            continue
        for imp_classe in in_dicc[classe]:
            out_dicc[imp_classe] = classe
    return json.dumps(out_dicc)


class Changes:
    AddAlumne = namedtuple('AddAlumne', ['nom', 'cognoms', 'classe'])
    MoveAlumne = namedtuple('MoveAlumne', ['alumne', 'a_classe'])
    DeleteAlumne = namedtuple('DeleteAlumne', ['alumne'])
    DeleteClasse = namedtuple('DeleteClasse', ['classe'])
    # "No operation", no fer res
    NoopAlumne = namedtuple('NoopAlumne', ['alumne'])

    def __init__(self):
        self.add = []
        self.move = []
        self.delete = []
        self.delete_classe = []
        self.noop = []

    def apply(self):
        with transaction.atomic():
            for addalu in self.add:
                alumne = Alumne.objects.update_or_create(
                    nom=addalu.nom,
                    cognoms=addalu.cognoms,
                    defaults={
                        'classe': addalu.classe
                    })[0]
                profile = Profile.objects.get_or_create(alumne=alumne)[0]
                if not profile.unregisteredUser and not profile.user:
                    uuser = UnregisteredUser.objects.get_or_create(
                        username=gen_username(alumne),
                        defaults={
                            'codi': gen_codi()
                        })[0]
                    profile.unregisteredUser = uuser
                    profile.save()
            for movealu in self.move:
                movealu.alumne.classe = movealu.a_classe
                movealu.alumne.save()
            for delalu in self.delete:
                delalu.alumne.delete()
            for delclasse in self.delete_classe:
                delclasse.classe.delete()

    @staticmethod
    def _get_classe(cmap, icls):
        for classe in cmap:
            if cmap[classe] is None:
                continue
            if icls in cmap[classe]:
                return classe
        raise KeyError("Entrada invàlida: {}. S'esperava la classe: {}".format(
            cmap, icls))

    @classmethod
    def calculate(cls, imp, cmap, delete_other=True):
        ins = cls()
        pdata = parse(validate(imp))

        for palumne in pdata:
            classe = Classe.objects.get(
                id_interna=cls._get_classe(cmap, palumne.classe))
            try:
                alumne = Alumne.objects.get(
                    nom=palumne.nom, cognoms=palumne.cognoms)
            except Alumne.DoesNotExist:
                ins.add.append(
                    cls.AddAlumne(
                        nom=palumne.nom,
                        cognoms=palumne.cognoms,
                        classe=classe))
                continue
            if alumne.classe == classe:
                ins.noop.append(cls.NoopAlumne(alumne))
            else:
                ins.move.append(cls.MoveAlumne(alumne=alumne, a_classe=classe))

        if not delete_other:
            return ins

        for alumne in Alumne.objects.all():
            if not (alumne in (o.alumne for o in ins.move)
                    or alumne in (o.alumne for o in ins.noop)):
                ins.delete.append(cls.DeleteAlumne(alumne))

        for classe in Classe.objects.all():
            if classe.id_interna not in cmap or not cmap[classe.id_interna]:
                ins.delete_classe.append(cls.DeleteClasse(classe))

        return ins
