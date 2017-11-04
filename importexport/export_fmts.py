import csv
import json
import pickle
import pickletools
import gzip
from io import BytesIO
from usermanager.models import Profile
from .pklf import PickledInfo, PickledCurs, PickledClasse
from . import ampacsv
from . import aesencrypt


def export_csv(outfile, alumnes):
    fieldnames = [
        'First Name', 'Last Name', 'Birthday', 'E-mail Address',
        'E-mail 2 Address', 'E-mail 3 Address', 'Home Phone', 'Home Phone 2',
        'Home Phone 3', 'Categories'
    ]
    writer = csv.DictWriter(outfile, fieldnames)
    writer.writeheader()
    for alumne in alumnes:
        if alumne is None:
            continue
        writer.writerow({
            'First Name': alumne.nom,
            'Last Name': alumne.cognoms,
            'E-mail Address': alumne.correu_alumne,
            'E-mail 2 Address': alumne.correu_tutor_1,
            'E-mail 3 Address': alumne.correu_tutor_2,
            'Home Phone': alumne.telefon_alumne,
            'Home Phone 2': alumne.telefon_tutor_1,
            'Home Phone 3': alumne.telefon_tutor_2,
            'Categories': str(alumne.classe)
        })


def export_ampacsv(outfile, alumnes):
    writer = csv.DictWriter(
        outfile, ampacsv.FIELDNAMES, dialect=ampacsv.AmpaDialect())
    writer.writeheader()
    for alumne in alumnes:
        try:
            profile = Profile.objects.get(alumne=alumne)
            if profile.user:
                username = profile.user.username
            elif profile.unregisteredUser:
                username = profile.unregisteredUser.username
            else:
                username = '-'
        except Profile.DoesNotExist:
            username = '-'
        row = {
            'pk': alumne.pk,
            'Nom': alumne.nom,
            'Cognoms': alumne.cognoms,
            'Nom tutor 1': alumne.nom_tutor_1,
            'Cognoms tutor 1': alumne.cognoms_tutor_1,
            'Nom tutor 2': alumne.nom_tutor_2,
            'Cognoms tutor 2': alumne.cognoms_tutor_2,
            'Correu alumne': alumne.correu_alumne,
            'Compartir correu alumne': int(alumne.compartir_correu_alumne),
            'Correu tutor 1': alumne.correu_tutor_1,
            'Compartir correu tutor 1': int(alumne.compartir_correu_tutor_1),
            'Correu tutor 2': alumne.correu_tutor_2,
            'Compartir correu tutor 2': int(alumne.compartir_correu_tutor_2),
            'Telèfon alumne': alumne.telefon_alumne,
            'Compartir telèfon alumne': int(alumne.compartir_telefon_alumne),
            'Telèfon tutor 1': alumne.telefon_tutor_1,
            'Compartir telèfon tutor 1': int(alumne.compartir_telefon_tutor_1),
            'Telèfon tutor 2': alumne.telefon_tutor_2,
            'Compartir telèfon tutor 2': int(alumne.compartir_telefon_tutor_2),
            'Classe': alumne.classe.id_interna,
            'Curs': alumne.classe.curs.id_interna,
            'Usuari': username,
            'Eliminar': 0
        }
        writer.writerow(row)


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
    with gzip.GzipFile(fileobj=outfile, mode='ab') as gzfile:
        pickle.dump(optimize_pickle(info), gzfile, protocol=4)


def export_encrypted_pickle(outfile, password, classe=None):
    plain_pickle = BytesIO()
    export_pickle(plain_pickle, classe)
    plain_pickle.seek(0)
    outfile.write(b'AMPAAES0')
    init_vector = aesencrypt.gen_init_vector()
    outfile.write(init_vector)
    encrypt_params = aesencrypt.CryptoParams(password, init_vector)
    aesencrypt.encrypt(plain_pickle, outfile, encrypt_params)


def export_json(outfile, classe=None):
    info = gen_pickled_info(classe)
    json.dump(info.to_json(), outfile, indent=None, separators=(',', ':'))
