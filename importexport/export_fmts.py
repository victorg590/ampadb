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
            'Birthday': a.data_de_naixement,
            'E-mail Address': a.correu_alumne,
            'E-mail 2 Address': a.correu_pare,
            'E-mail 3 Address': a.correu_mare,
            'Home Phone': a.telefon_alumne,
            'Home Phone 2': a.telefon_pare,
            'Home Phone 3': a.telefon_mare,
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
            'Data de naixement': '',
            'Nom pare': a.nom_pare,
            'Cognoms pare': a.cognoms_pare,
            'Nom mare': a.nom_mare,
            'Cognoms mare': a.cognoms_mare,
            'Correu alumne': a.correu_alumne,
            'Compartir correu alumne': int(a.compartir_correu_alumne),
            'Correu pare': a.correu_pare,
            'Compartir correu pare': int(a.compartir_correu_pare),
            'Correu mare': a.correu_mare,
            'Compartir correu mare': int(a.compartir_correu_mare),
            'Telèfon alumne': a.telefon_alumne,
            'Compartir telèfon alumne': int(a.compartir_telefon_alumne),
            'Telèfon pare': a.telefon_pare,
            'Compartir telèfon pare': int(a.compartir_telefon_pare),
            'Telèfon mare': a.telefon_mare,
            'Compartir telèfon mare': int(a.compartir_telefon_mare),
            'Classe': a.classe.id_interna,
            'Curs': a.classe.curs.id_interna,
            'Usuari': username,
            'Eliminar': 0
        }
        if a.data_de_naixement:
            d['Data de naixement'] = a.data_de_naixement.strftime('%Y-%m-%d')
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
