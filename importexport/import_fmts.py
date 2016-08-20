import csv
import json
import pickle
import gzip
import pathlib
from datetime import datetime
from django.core.exceptions import ValidationError
from .forms import IEFormats
from contactboard.models import *
from usermanager.models import *
from django.db import transaction
from ampadb.support import gen_username, gen_codi, username_exists

class InvalidFormat(Exception):
    @classmethod
    def falta_columna(cls, columna):
        return cls('Falta columna: "{}"'.format(columna))

    @classmethod
    def falta_a_fila(cls, columna, fila):
        return cls('Falta columna {} a la fila {}'.format(columna, fila))

    @classmethod
    def invalid(cls, columna, fila, rao):
        return cls('{} invàlid a la fila {}: {}'.format(columna, fila, rao))

def detect_format(filename):
    """Detecta un format a partir la extensió.

    Si no es pot detectar, envía un `ValueError`
    """
    path = pathlib.PurePath(filename)
    if path.suffixes[-1] == '.csv':
        return IEFormats.AMPACSV
    elif path.suffixes[-1] == '.json':
        return IEFormats.JSON
    elif path.suffixes[-2:] == ['.pkl', '.gz']:
        return IEFormats.PICKLE
    else:
        raise ValueError

def _importar_fila(fila):
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
        eliminar = int(fila['Eliminar'])
        if eliminar not in [0, 1, 2]:
            raise ValueError
    except ValueError:
        raise InvalidFormat('"Eliminar" ha de estar buit o ser 0, 1 o 2 (fila: '
            + fila + ')')
    except KeyError:
        eliminar = 0

    if eliminar == 1:
        if not usuari_existia:
            return None
        alumne.delete()
        return None
    elif eliminar == 2:
        if not usuari_existia:
            return None
        try:
            profile = Profile.objects.get(alumne=alumne)
            if profile.user:
                profile.user.delete()
            if profile.unregisteredUser:
                profile.unregisteredUser.delete()
        except Profile.DoesNotExist:
            pass
        alumne.delete()
        return None

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
        if not ddn_temp and usuari_existia:
            data_de_naixement = None
        else:
            data_de_naixement = datetime.strptime(ddn_temp, '%Y-%m-%d')
    except KeyError:
        if usuari_existia:
            data_de_naixement = None
        else:
            raise InvalidFormat.falta_columna('Data de naixement')
    except ValueError:
        raise InvalidFormat.invalid('Data de naixement', fila,
            ". S'espera el format 'YYYY-MM-DD'.")
    if data_de_naixement:
        alumne.data_de_naixement = data_de_naixement

    try:
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
            raise InvalidFormat.invalid('Correu alumne', fila, exc[0])

    try:
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
        alumne.telefon_pare = fila['Teléfon pare']
        alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['telefon_pare']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Teléfon pare', fila, exc[0])

    try:
        alumne.telefon_mare = fila['Teléfon mare']
        alumne.clean_fields()
    except KeyError:
        pass
    except ValidationError as e:
        try:
            exc = e['telefon_mare']
        except KeyError:
            exc = None
        if exc:
            raise InvalidFormat.invalid('Teléfon mare', fila, exc[0])

    try:
        if fila['Compartir'] and bool(int(fila['Compartir'])):
            alumne.compartir = True
        else:
            alumne.compartir = False
    except KeyError:
        alumne.compartir = False
    except ValueError:
        raise InvalidFormat.invalid('Compartir', fila, 'Ha de ser 0 o 1')

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
            try:
                curs = Curs.objects.get(id_interna=curs_id)
            except Curs.DoesNotExist:
                curs = Curs(nom=curs_id, id_interna=curs_id)
                curs.save()
            classe = Classe(nom=classe_id, id_interna=classe_id, curs=curs)
            classe.save()
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
                return alumne.pk
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
                user = UnregisteredUser(username=username,
                    codi=gen_codi())
                user.save()
                alumne.save()
                profile = Profile(alumne=alumne, unregisteredUser=user)
                profile.save()
        else:
            user = UnregisteredUser(username=username, codi=gen_codi())
            user.save()
            alumne.save()
            profile = Profile(alumne=alumne, unregisteredUser=user)
            profile.save()
    alumne.save()
    return alumne.pk

def import_ampacsv(infile):
    reader = csv.DictReader(infile, dialect=ampacsv.AmpaDialect())
    with transaction.atomic():
        for fila in reader:
            _importar_fila(fila)

def import_excel(infile):
    reader = csv.DictReader(infile, dialect='excel')
    with transaction.atomic():
        for fila in reader:
            _importar_fila(fila)

def import_json(infile):
    date_format = '%Y-%m-%d'
    top_dict = json.load(infile)
    try:
        for c in top_dict['cursos']:
            curs_dict = top_dict['cursos'][c]
            try:
                curs = Curs.objects.get(id_interna=c)
            except Curs.DoesNotExist:
                curs = Curs(id_interna=c)
            curs.nom = curs_dict['nom']
            curs.ordre = curs_dict['ordre']
            curs.save()
            for cl in curs_dict['classes']:
                classe_dict = curs_dict['classes'][cl]
                try:
                    classe = Classe.objects.get(id_interna=cl)
                except Classe.DoesNotExist:
                    classe = Classe(id_interna=cl)
                classe.nom = classe_dict['nom']
                classe.curs = curs
                classe.save()
                for a in classe_dict['alumnes']:
                    try:
                        alumne = Alumne.objects.get(pk=a['pk'])
                    except Alumne.DoesNotExist:
                        alumne = Alumne(pk=a['pk'])
                    alumne.nom = a['nom']
                    alumne.cognoms = a['cognoms']
                    alumne.data_de_naixement = datetime.strptime(
                        a['data_de_naixement'], date_format)
                    alumne.correu_alumne = a['correu_alumne']
                    alumne.correu_pare = a['correu_pare']
                    alumne.correu_mare = a['correu_mare']
                    alumne.telefon_pare = a['telefon_pare']
                    alumnne.telefon_mare = a['telefon_mare']
                    alumne.classe = classe
                    alumne.save()
        for u in top_dict['usuaris']:
            user_dict = top_dict['usuaris'][u]
            try:
                user = User.objects.get(username=u)
            except User.DoesNotExist:
                user = User(username=u)
            user.password = user_dict['password']
            user.is_staff = user_dict['is_staff']
            user.is_superuser = user_dict['is_superuser']
            user.save()
            if user_dict['alumne']:
                try:
                    profile = Profile.objects.get(user=user)
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                try:
                    profile.alumne = Alumne.objects.get(pk=user_dict['alumne'])
                except Alumne.DoesNotExist:
                    raise InvalidFormat('Referència a un alumne que no'
                        ' existeix: ' + str(user_dict['alumne']))
                profile.save()
        for uu in top_dict['uu']:
            uu_dict = top_dict['uu'][uu]
            try:
                user = UnregisteredUser.objects.get(username=uu)
            except UnregisteredUser.DoesNotExist:
                user = UnregisteredUser(username=uu)
            user.codi = uu_dict['codi']
            user.save()
            if uu_dict['alumne']:
                try:
                    profile = Profile.objects.get(user=user)
                except Profile.DoesNotExist:
                    profile = Profile(unregisteredUser=user)
                try:
                    profile.alumne = Alumne.objects.get(pk=user_dict['alumne'])
                except Alumne.DoesNotExist:
                    raise InvalidFormat('Referència a un alumne que no'
                        ' existeix: ' + str(uu_dict['alumne']))
    except KeyError as e:
        raise InvalidFormat('Falta clau: ' + e)

def import_pickle(infile):
    with gzip.GzipFile(fileobj=infile) as gz:
        return import_pickle_uncompressed(gz)

def import_pickle_uncompressed(infile):
    info = pickle.load(infile)
    try:
        if info.VERSION != 1:
            raise InvalidFormat('Versió invàlida')
        for curs in info.cursos:
            curs.unpickle()
            for classe in curs.classes:
                classe.unpickle()
                for alumne in classe.alumnes:
                    alumne.unpickle()
        for user in info.users:
            user.unpickle()
        for uu in info.uu:
            uu.unpickle()
    except InvalidFormat:
        raise
    except:
        raise InvalidFormat("No és un arxiu Pickle d'aquesta aplicació")
