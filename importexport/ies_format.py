import csv
import json
from collections import namedtuple
from .import_fmts import InvalidFormat, bytestream_to_text
from contactboard.models import Classe, Alumne
from usermanager.models import Profile, UnregisteredUser
from ampadb.support import gen_username, gen_codi
from django.db import transaction

ImportedAlumne = namedtuple('ImportedAlumne', ['nom', 'cognoms', 'classe'])


def validate_row(row):
    try:
        nom = row['NOM'].strip()
    except KeyError as e:
        raise InvalidFormat.falta_columna('NOM') from e
    if not nom:
        raise InvalidFormat.falta_a_fila('NOM', row)

    try:
        cognom1 = row['COGNOM 1'].strip()
    except KeyError as e:
        raise InvalidFormat.falta_columna('COGNOM 1') from e
    if not cognom1:
        raise InvalidFormat.falta_a_fila('COGNOM 1', row)

    # COGNOM 2 opcional

    try:
        classe = row['CLASSE'].strip()
    except KeyError as e:
        raise InvalidFormat.falta_columna('CLASSE') from e
    if not classe:
        raise InvalidFormat.falta_a_fila('CLASSE', row)


def validate(inp):
    try:
        reader = csv.DictReader(bytestream_to_text(inp))
    except UnicodeDecodeError as e:
        raise InvalidFormat('No és un arxiu de text (UTF-8)') from e
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
    for a in parsed_inp:
        current |= {a.classe}
    return current


def val_json(inp, dicc):
    current = set()
    expected = unique_classes(parse(validate(inp)))
    for k in dicc:
        if not Classe.objects.filter(id_interna=k).exists():
            raise InvalidFormat('No existeix la classe "{}"'.format(k))
        if dicc[k] is None:
            continue
        for c in dicc[k]:
            if c in current:
                raise InvalidFormat('Classe repetida: "{}"'.format(c))
            if c not in expected:
                raise InvalidFormat('Classe no esperada: "{}"'.format(c))
            current |= {c}
    if current < expected:
        raise InvalidFormat('Falten classes: {}'.format(expected - current))
    assert current == expected


def rev_json(in_dicc):
    if in_dicc is None:
        return json.dumps(None)
    out_dicc = {}
    for k in in_dicc:
        if in_dicc[k] is None:
            continue
        for c in in_dicc[k]:
            out_dicc[c] = k
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
            for a in self.add:
                alumne, nou = Alumne.objects.get_or_create(
                    nom=a.nom, cognoms=a.cognoms,
                    defaults={'classe': a.classe}
                )
                if not nou:
                    alumne.classe = a.classe
                    alumne.save()
                profile = Profile.objects.get_or_create(alumne=alumne)[0]
                if not profile.unregisteredUser and not profile.user:
                    uu = UnregisteredUser.objects.get_or_create(
                        username=gen_username(alumne),
                        defaults={'codi': gen_codi()}
                    )[0]
                    profile.unregisteredUser = uu
            for m in self.move:
                m.alumne.classe = m.a_classe
                m.alumne.save()
            for d in self.delete:
                d.alumne.delete()
            for dc in self.delete_classe:
                dc.classe.delete()

    @staticmethod
    def _get_classe(cmap, icls):
        for c in cmap:
            if cmap[c] is None:
                continue
            if icls in cmap[c]:
                return c
        raise KeyError("Entrada invàlida: {}. S'esperava la classe: {}".format(
            cmap, icls))

    @classmethod
    def calculate(cls, imp, cmap, delete_other=True):
        ins = cls()
        pdata = parse(validate(imp))

        for c in cmap:
            if cmap[c] is None:
                classe = Classe.objects.get(id_interna=c)
                ins.delete_classe.append(cls.DeleteClasse(classe))

        for palumne in pdata:
            classe = Classe.objects.get(id_interna=cls._get_classe(cmap,
                                        palumne.classe))
            try:
                alumne = Alumne.objects.get(nom=palumne.nom,
                                            cognoms=palumne.cognoms)
            except Alumne.DoesNotExist:
                ins.add.append(cls.AddAlumne(nom=palumne.nom,
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
            if not (
                alumne in (o.alumne for o in ins.move) or
                alumne in (o.alumne for o in ins.noop)
            ):
                ins.delete.append(cls.DeleteAlumne(alumne))
        return ins
