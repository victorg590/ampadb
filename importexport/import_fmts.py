import csv
import json
import pickle
import gzip
import pathlib
import tempfile
from datetime import datetime
from django.core.exceptions import ValidationError
from .forms import IEFormats
from contactboard.models import *
from usermanager.models import *
from extraescolars.models import *
from missatges.models import *
from django.contrib.auth.models import User
from django.db import transaction
from ampadb.support import gen_username, gen_codi, username_exists
from . import ampacsv
from .pklf import CURRENT_VERSION, PickledInfo

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
        raise InvalidFormat('"Eliminar" ha de estar buit o ser 0, 1 o 2 (fila: '
            + str(fila) + ')')
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
        ddn_temp = fila['Data de naixement']
        if ddn_temp:
            data_de_naixement = datetime.strptime(ddn_temp, '%Y-%m-%d')
        else:
            data_de_naixement = None
    except KeyError:
        if usuari_existia:
            data_de_naixement = None
        else:
            raise InvalidFormat.falta_columna('Data de naixement')
    except ValueError:
        raise InvalidFormat.invalid('Data de naixement', fila,
            "S'espera el format 'YYYY-MM-DD'.")
    if data_de_naixement:
        alumne.data_de_naixement = data_de_naixement

    try:
        if fila['Nom pare']:
            alumne.nom_pare = fila['Nom pare']
    except KeyError:
        pass

    try:
        if fila['Cognoms pare']:
            alumne.cognoms_pare = fila['Cognoms pare']
    except KeyError:
        pass

    try:
        if fila['Nom mare']:
            alumne.nom_mare = fila['Nom mare']
    except KeyError:
        pass

    try:
        if fila['Cognoms mare']:
            alumne.cognoms_mare = fila['Cognoms mare']
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
        if fila['Correu pare']:
            alumne.correu_pare = fila['Correu pare']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['correu_pare']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Correu pare', fila, exc[0])

    try:
        tmp = fila['Compartir correu pare']
        alumne.compartir_correu_pare = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_correu_pare = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir correu pare', fila,
            'Ha de ser 0 o 1')

    try:
        if fila['Correu mare']:
            alumne.correu_mare = fila['Correu mare']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['correu_mare']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Correu mare', fila, exc[0])

    try:
        tmp = fila['Compartir correu mare']
        alumne.compartir_correu_mare = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_correu_mare = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir correu mare', fila,
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
        if fila['Telèfon pare']:
            alumne.telefon_pare = fila['Telèfon pare']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['telefon_pare']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Telèfon pare', fila, exc[0])

    try:
        tmp = fila['Compartir telèfon pare']
        alumne.compartir_telefon_pare = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_telefon_pare = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir telèfon pare', fila,
            'Ha de ser 0 o 1')

    try:
        if fila['Telèfon mare']:
            alumne.telefon_mare = fila['Telèfon mare']
            alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['telefon_mare']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Telèfon mare', fila, exc[0])

    try:
        tmp = fila['Compartir telèfon mare']
        alumne.compartir_telefon_mare = bool(tmp and int(tmp))
    except KeyError:
        alumne.compartir_telefon_mare = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir telèfon mare', fila,
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
                        Profile.objects.create(alumne=alumne, user=user)
                    else:
                        alumne.save()
                        Profile.objects.create(alumne=alumne,
                            unregisteredUser=user)
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
    alumnes = {d['alumne'] for d in afegits if d['alumne'] != None}
    classes = {d['classe'] for d in afegits if d['classe'] != None}
    classes |= {Alumne.objects.only('classe').get(pk=a).classe.pk
        for a in alumnes}
    cursos = {d['curs'] for d in afegits if d['curs'] != None}
    cursos |= {Classe.objects.only('curs').get(pk=c).curs.pk
        for c in classes}
    usuaris = {d['user'] for d in afegits if d['user'] != None}
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

def import_pickle(infile, preexistents=''):
    try:
        with gzip.GzipFile(fileobj=infile) as gz:
            return import_pickle_uncompressed(gz, preexistents)
    except OSError:
        # Prova per si no està comprimit
        return import_pickle_uncompressed(infile, preexistents)

def import_pickle_uncompressed(infile, preexistents=''):
    try:
        info = pickle.load(infile)
    except pickle.UnpicklingError:
        raise InvalidFormat('No és un arxiu Pickle')
    try:
        info.check_version(CURRENT_VERSION)
        info.unpickle(preexistents)
    except InvalidFormat:
        raise
    except Exception as e:
        raise InvalidFormat("No és un arxiu Pickle d'aquesta aplicació (" +
            str(e) + ')') from e
