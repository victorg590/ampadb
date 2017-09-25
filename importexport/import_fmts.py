import csv
import json
import pickle
import gzip
import pathlib
import tempfile
from datetime import datetime
from django.core.exceptions import ValidationError
from contactboard.models import *
from usermanager.models import *
from extraescolars.models import *
from missatges.models import *
from django.contrib.auth.models import User
from django.db import transaction
from ampadb.support import gen_username, gen_codi, username_exists
from . import ampacsv
from .pklf import CURRENT_VERSION, PickledInfo
from . import aesencrypt
from io import BytesIO


class InvalidFormat(Exception):
    @classmethod
    def falta_columna(cls, columna):
        return cls('Falta columna: "{}"'.format(columna))

    @classmethod
    def falta_a_fila(cls, columna, fila):
        return cls('Falta columna {} a la fila {}'.format(columna,
                   str(fila)))

    @classmethod
    def invalid(cls, columna, fila, rao):
        return cls('{} invàlid a la fila {}: {}'.format(columna, str(fila),
                   rao))


def bytestream_to_text(bytestream, encoding='utf-8'):
    textstream = tempfile.TemporaryFile(mode='w+t')
    for chunk in bytestream.chunks():
        decoded_chunk = chunk.decode(encoding)
        textstream.write(decoded_chunk)
    textstream.seek(0)
    return textstream

from .forms import IEFormats  # Aquí per a evitar dependències circulars # nopep8


def detect_format(filename):
    """Detecta un format a partir la extensió.

    Si no es pot detectar, envía un `ValueError`
    """
    path = pathlib.PurePath(filename)
    if len(path.suffixes) < 1:
        raise ValueError
    if path.suffixes[-1] == '.csv':
        return IEFormats.AMPACSV
    elif path.suffixes[-1] == '.json':
        return IEFormats.JSON
    elif path.suffixes[-2:] == ['.pkl', '.gz']:
        return IEFormats.PICKLE
    elif path.suffixes[-3:] == ['.pkl', '.gz', '.aes']:
        return IEFormats.PICKLE
    else:
        raise ValueError


def _importar_fila(fila):
    ret = {'alumne': None, 'classe': None, 'curs': None, 'user': None}
    try:
        pk = int(fila['pk'])
    except (ValueError, KeyError):
        pk = None
    if pk:
        try:
            alumne = Alumne.objects.get(pk=pk)
            usuari_existia = True
        except Alumne.DoesNotExist:
            alumne = Alumne(pk=pk)
            usuari_existia = False
    else:
        alumne = Alumne()
        usuari_existia = False

    try:
        eliminar = int(fila['Eliminar'] or 0)
        if eliminar not in [0, 1, 2]:
            raise ValueError
    except ValueError:
        raise InvalidFormat('"Eliminar" ha de estar buit o ser 0, 1 o 2 (fila:'
                            ' ' + str(fila) + ')')
    except KeyError:
        eliminar = 0

    if eliminar == 1:
        if not usuari_existia:
            return ret
        alumne.delete()
        return ret
    elif eliminar == 2:
        if not usuari_existia:
            return ret
        try:
            profile = Profile.objects.get(alumne=alumne)
            if profile.user:
                profile.user.delete()
            if profile.unregisteredUser:
                profile.unregisteredUser.delete()
        except Profile.DoesNotExist:
            pass
        alumne.delete()
        return ret

    try:
        nom = fila['Nom']
    except KeyError:
        if usuari_existia:
            nom = None
        else:
            raise InvalidFormat.falta_columna('Nom')
    if not (nom or usuari_existia):
            raise InvalidFormat.falta_a_fila('Nom', fila)
    if nom:
        alumne.nom = nom

    try:
        cognoms = fila['Cognoms']
    except KeyError:
        if usuari_existia:
            cognoms = None
        else:
            raise InvalidFormat.falta_columna('Cognoms')
    if not (cognoms or usuari_existia):
        raise InvalidFormat.falta_a_fila('Cognoms', fila)
    if cognoms:
        alumne.cognoms = cognoms

    try:
        if fila['Nom tutor 1']:
            alumne.nom_tutor_1 = fila['Nom tutor 1']
    except KeyError:
        pass

    try:
        if fila['Cognoms tutor 1']:
            alumne.cognoms_tutor_1 = fila['Cognoms tutor 1']
    except KeyError:
        pass

    try:
        if fila['Nom tutor 2']:
            alumne.nom_tutor_2 = fila['Nom tutor 2']
    except KeyError:
        pass

    try:
        if fila['Cognoms tutor 2']:
            alumne.cognoms_tutor_2 = fila['Cognoms tutor 2']
    except KeyError:
        pass

    try:
        if fila['Correu alumne']:
            alumne.correu_alumne = fila['Correu alumne']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['correu_alumne']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Correu alumne', fila, exc)

    try:
        tmp = fila['Compartir correu alumne']
        alumne.compartir_correu_alumne = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_correu_alumne = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir correu alumne', fila,
                                    'Ha de ser 0 o 1')

    try:
        if fila['Correu tutor 1']:
            alumne.correu_tutor_1 = fila['Correu tutor 1']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['correu_tutor_1']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Correu tutor 1', fila, exc[0])

    try:
        tmp = fila['Compartir correu tutor 1']
        alumne.compartir_correu_tutor_1 = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_correu_tutor_1 = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir correu tutor 1', fila,
                                    'Ha de ser 0 o 1')

    try:
        if fila['Correu tutor 2']:
            alumne.correu_tutor_2 = fila['Correu tutor 2']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['correu_tutor_2']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Correu tutor 2', fila, exc[0])

    try:
        tmp = fila['Compartir correu tutor 2']
        alumne.compartir_correu_tutor_2 = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_correu_tutor_2 = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir correu tutor 2', fila,
                                    'Ha de ser 0 o 1')

    try:
        if fila['Telèfon alumne']:
            alumne.telefon_alumne = fila['Telèfon alumne']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['telefon_alumne']
        except KeyError:
            pass
        else:
            raise InvalidFormat.invalid('Telèfon alumne', fila, exc[0])

    try:
        tmp = fila['Compartir telèfon alumne']
        alumne.compartir_telefon_alumne = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_telefon_alumne = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir telèfon alumne', fila,
                                    'Ha de ser 0 o 1')

    try:
        if fila['Telèfon tutor 1']:
            alumne.telefon_tutor_1 = fila['Telèfon tutor 1']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['telefon_tutor_1']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Telèfon tutor 1', fila, exc[0])

    try:
        tmp = fila['Compartir telèfon tutor 1']
        alumne.compartir_telefon_tutor_1 = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_telefon_tutor_1 = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir telèfon tutor 1', fila,
                                    'Ha de ser 0 o 1')

    try:
        if fila['Telèfon tutor 2']:
            alumne.telefon_tutor_2 = fila['Telèfon tutor 2']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['telefon_tutor_2']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Telèfon tutor 2', fila, exc[0])

    try:
        tmp = fila['Compartir telèfon tutor 2']
        alumne.compartir_telefon_tutor_2 = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_telefon_tutor_2 = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir telèfon tutor 2', fila,
                                    'Ha de ser 0 o 1')

    try:
        curs_id = fila['Curs']
    except KeyError:
        curs_id = None

    try:
        classe_id = fila['Classe']
    except KeyError:
        if usuari_existia:
            classe_id = None
        else:
            raise InvalidFormat.falta_columna('Classe')
    if not (classe_id or usuari_existia):
        raise InvalidFormat.falta_a_fila('Classe', fila)
    if classe_id:
        try:
            alumne.classe = Classe.objects.get(id_interna=classe_id)
        except Classe.DoesNotExist:
            if not curs_id:
                raise InvalidFormat('"Classe" no existeix, però tampoc es'
                                    ' defineix "Curs" (fila: {})'.format(fila))
            curs = Curs.objects.get_or_create(id_interna=curs_id,
                                              defaults={'nom': curs_id})[0]
            classe = Classe(nom=classe_id, id_interna=classe_id, curs=curs)
            classe.save()
            ret['classe'] = classe.pk
            ret['curs'] = curs.pk
            alumne.classe = classe

    try:
        username = fila['Usuari']
    except KeyError:
        if usuari_existia:
            try:
                profile = Profile.objects.get(alumne=alumne)
                if not (profile.user or profile.unregisteredUser):
                    raise Profile.DoesNotExist
                alumne.save()
                ret['alumne'] = alumne.pk
                return ret
            except Profile.DoesNotExist:
                username = ''
        else:
            username = ''
    if not username:
        username = gen_username(alumne)
    if username != '-':
        if username_exists(username):
            try:
                user = User.objects.get(username=username)
                registered = True
            except User.DoesNotExist:
                try:
                    user = UnregisteredUser.objects.get(
                        username=username)
                    registered = False
                except UnregisteredUser.DoesNotExist:
                    username = gen_username(alumne)
                    user = None
            if user:
                try:
                    if registered:
                        profile = Profile.objects.get(user=user)
                    else:
                        profile = Profile.objects.get(
                            unregisteredUser=user)
                    if profile.alumne != alumne:
                        username = gen_username(alumnne)
                        user = None
                except Profile.DoesNotExist:
                    if registered:
                        alumne.save()
                        Profile.objects.update_or_create(
                            alumne=alumne,
                            defaults={'user': user}
                        )
                    else:
                        alumne.save()
                        Profile.objects.update_or_create(
                            alumne=alumne,
                            defaults={'unregisteredUser': user})
            if user is None:
                user = UnregisteredUser.objects.create(username=username,
                                                       codi=gen_codi())
                ret['user'] = user.pk
                alumne.save()
                Profile.objects.update_or_create(alumne=alumne, defaults={
                    'unregisteredUser': user, 'user': None})
        else:
            user = UnregisteredUser.objects.create(username=username,
                                                   codi=gen_codi())
            ret['user'] = user.pk
            alumne.save()
            Profile.objects.update_or_create(alumne=alumne, defaults={
                'unregisteredUser': user, 'user': None})
    alumne.save()
    ret['alumne'] = alumne.pk
    return ret


def _csv_del_all():
    Alumne.objects.all().delete()
    Classe.objects.all().delete()
    Curs.objects.all().delete()
    User.objects.exclude(is_staff=True, is_superuser=True).delete()
    UnregisteredUser.objects.all().delete()
    Profile.objects.all().delete()


def _csv_del_not_added(afegits):
    alumnes = {d['alumne'] for d in afegits if d['alumne'] is not None}
    classes = {d['classe'] for d in afegits if d['classe'] is not None}
    classes |= {Alumne.objects.only('classe').get(pk=a).classe.pk
                for a in alumnes}
    cursos = {d['curs'] for d in afegits if d['curs'] is not None}
    cursos |= {Classe.objects.only('curs').get(pk=c).curs.pk
               for c in classes}
    usuaris = {d['user'] for d in afegits if d['user'] is not None}
    for a in alumnes:
        try:
            p = Profile.objects.get(alumne__pk=a).unregisteredUser.pk
            usuaris |= {p}
        except Profile.DoesNotExist:
            pass

    Alumne.objects.exclude(pk__in=alumnes).delete()
    Classe.objects.exclude(pk__in=classes).delete()
    Curs.objects.exclude(pk__in=cursos).delete()
    UnregisteredUser.objects.exclude(pk__in=usuaris).delete()
    User.objects.exclude(is_staff=True, is_superuser=True).delete()


def import_ampacsv(infile, preexistents=''):
    reader = csv.DictReader(infile, dialect=ampacsv.AmpaDialect())
    with transaction.atomic():
        if preexistents == 'DEL_ALL':
            _csv_del_all()
        afegits = []
        for fila in reader:
            afegits.append(_importar_fila(fila))
        if preexistents == 'DEL':
            _csv_del_not_added(afegits)


def import_excel(infile, preexistents=''):
    reader = csv.DictReader(infile, dialect='excel')
    with transaction.atomic():
        if preexistents == 'DEL_ALL':
            _csv_del_all()
        afegits = []
        for fila in reader:
            afegits.append(_importar_fila(fila))
        if preexistents == 'DEL':
            _csv_del_not_added(afegits)


def import_json(infile, preexistents=''):
    try:
        info = PickledInfo.from_json(json.load(infile))
        info.unpickle(preexistents)
    except InvalidFormat:
        raise
    except Exception as e:
        raise InvalidFormat("No és un arxiu JSON d'aquesta aplicació (" +
                            str(e) + ')') from e


def decrypt_pickle(infile, password):
    if infile.read(len(b'AMPAAES0')) != b'AMPAAES0':
        raise InvalidFormat('No està xifrat o no és un arxiu de'
                            'còpia de seguretat')
    iv = infile.read(aesencrypt.IV_LENGTH)
    plain_pickle = BytesIO()
    aesencrypt.decrypt(infile, plain_pickle,password, iv)
    return plain_pickle

def import_pickle(infile, password, preexistents=''):
    if password:
        plain_pickle = decrypt_pickle(infile, password)
    else:
        plain_pickle = infile
    try:
        try:
            plain_pickle.seek(0)
            with gzip.GzipFile(fileobj=plain_pickle) as gz:
                return import_pickle_uncompressed(gz, password != '',
                                                  preexistents)
        except OSError:
            # Prova per si no està comprimit
            return import_pickle_uncompressed(infile, password != '',
                                              preexistents)
    except EOFError:
        raise InvalidFormat(
            'Contrasenya incorrecta o no és un arxiu Pickle' if password
            else 'No és un arxiu Pickle'
        )


def import_pickle_uncompressed(infile, encrypted, preexistents=''):
    try:
        info = pickle.load(infile)
    except pickle.UnpicklingError:
        raise InvalidFormat(
            'Contrasenya incorrecta o no és un arxiu Pickle' if encrypted
            else 'No és un arxiu Pickle'
        )
    try:
        info.check_version(CURRENT_VERSION)
        info.unpickle(preexistents)
    except InvalidFormat:
        raise
    except Exception as e:
        raise InvalidFormat("No és un arxiu Pickle d'aquesta aplicació (" +
                            str(e) + ')') from e
