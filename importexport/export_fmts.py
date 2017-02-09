import csv
import json
import pickle
import pickletools
import gzip
from contactboard.models import *
from usermanager.models import *
from django.contrib.auth.models import User
from .pklf import *
from . import ampacsv


def export_csv(outfile, alumnes):
    fieldnames = ['First Name', 'Last Name', 'Birthday', 'E-mail Address',
                  'E-mail 2 Address', 'E-mail 3 Address', 'Home Phone',
                  'Home Phone 2', 'Home Phone 3', 'Categories']
    writer = csv.DictWriter(outfile, fieldnames)
    writer.writeheader()
    for a in alumnes:
        if a is None:
            continue
        writer.writerow({
            'First Name': a.nom,
            'Last Name': a.cognoms,
            'E-mail Address': a.correu_alumne,
            'E-mail 2 Address': a.correu_tutor_1,
            'E-mail 3 Address': a.correu_tutor_2,
            'Home Phone': a.telefon_alumne,
            'Home Phone 2': a.telefon_tutor_1,
            'Home Phone 3': a.telefon_tutor_2,
            'Categories': str(a.classe)
        })


def export_ampacsv(outfile, alumnes):
    writer = csv.DictWriter(outfile, ampacsv.fieldnames,
                            dialect=ampacsv.AmpaDialect())
    writer.writeheader()
    for a in alumnes:
        try:
            profile = Profile.objects.get(alumne=a)
            if profile.user:
                username = profile.user.username
            elif profile.unregisteredUser:
                username = profile.unregisteredUser.username
            else:
                username = '-'
        except Profile.DoesNotExist:
            username = '-'
        d = {
            'pk': a.pk,
            'Nom': a.nom,
            'Cognoms': a.cognoms,
            'Nom tutor 1': a.nom_tutor_1,
            'Cognoms tutor 1': a.cognoms_tutor_1,
            'Nom tutor 2': a.nom_tutor_2,
            'Cognoms tutor 2': a.cognoms_tutor_2,
            'Correu alumne': a.correu_alumne,
            'Compartir correu alumne': int(a.compartir_correu_alumne),
            'Correu tutor 1': a.correu_tutor_1,
            'Compartir correu tutor 1': int(a.compartir_correu_tutor_1),
            'Correu tutor 2': a.correu_tutor_2,
            'Compartir correu tutor 2': int(a.compartir_correu_tutor_2),
            'Telèfon alumne': a.telefon_alumne,
            'Compartir telèfon alumne': int(a.compartir_telefon_alumne),
            'Telèfon tutor 1': a.telefon_tutor_1,
            'Compartir telèfon tutor 1': int(a.compartir_telefon_tutor_1),
            'Telèfon tutor 2': a.telefon_tutor_2,
            'Compartir telèfon tutor 2': int(a.compartir_telefon_tutor_2),
            'Classe': a.classe.id_interna,
            'Curs': a.classe.curs.id_interna,
            'Usuari': username,
            'Eliminar': 0
        }
        writer.writerow(d)


def optimize_pickle(nopkl, protocol=4):
    pkl = pickle.dumps(nopkl, protocol=protocol)
    return pickle.loads(pickletools.optimize(pkl))


def gen_pickled_info(classe=None):
    if classe is None:
        return PickledInfo.transform()
    info = PickledInfo()
    curs = PickledCurs.transform(classe.curs, False)
    info.cursos.append(curs)
    curs.classes.append(PickledClasse.transform(classe))
    return info


def export_pickle(outfile, classe=None):
    info = gen_pickled_info(classe)
    with gzip.GzipFile(fileobj=outfile, mode='ab') as gz:
        pickle.dump(optimize_pickle(info), gz, protocol=4)


def export_json(outfile, classe=None):
    info = gen_pickled_info(classe)
    json.dump(info.to_json(), outfile, indent=None, separators=(',', ':'))
