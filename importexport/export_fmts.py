from tempfile import TemporaryFile
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
        'E-mail 2 Address', 'E-mail 3 Address', 'Home Phone', 'Home Phone 2',
        'Categories']
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
            'Home Phone': a.telefon_pare,
            'Home Phone 2': a.telefon_mare,
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
        writer.writerow({
            'pk': a.pk,
            'Nom': a.nom,
            'Cognoms': a.cognoms,
            'Data de naixement': a.data_de_naixement.strftime('%Y-%m-%d'),
            'Correu alumne': a.correu_alumne,
            'Correu pare': a.correu_pare,
            'Correu mare': a.correu_mare,
            'Teléfon pare': a.telefon_pare,
            'Teléfon mare': a.telefon_mare,
            'Compartir': int(a.compartir),
            'Classe': a.classe.id_interna,
            'Curs': a.classe.curs.id_interna,
            'Usuari': username,
            'Eliminar': 0
        })

def export_json(outfile):
    date_format = '%Y-%m-%d'
    top_dict = {'cursos': {}, 'usuaris': {}, 'uu': {}}
    for c in Curs.objects.all():
        curs_dict = {'nom': c.nom, 'ordre': c.ordre,
            'classes': {}}
        for cl in Classe.objects.filter(curs=c):
            classe_dict = {'nom': cl.nom, 'alumnes': []}
            for a in Alumne.objects.filter(classe=cl):
                alumne_dict = {'pk': a.pk, 'nom': a.nom, 'cognoms': a.cognoms,
                    'data_de_naixement': a.data_de_naixement.strftime(date_format),
                    'correu_alumne': a.correu_alumne,
                    'correu_pare': a.correu_pare, 'correu_mare': a.correu_mare,
                    'telefon_pare': a.telefon_pare,
                    'telefon_mare': a.telefon_mare, 'compartir': a.compartir}
                classe_dict['alumnes'].append(alumne_dict)
            curs_dict['classes'][cl.id_interna] = classe_dict
        top_dict['cursos'][c.id_interna] = curs_dict
    for u in User.objects.all():
        user_dict = {'password': u.password, 'is_staff': u.is_staff,
            'is_superuser': u.is_superuser}
        try:
            profile = Profile.objects.get(user=u)
            user_dict['alumne'] = profile.alumne.pk
        except Profile.DoesNotExist:
            user_dict['alumne'] = None
        top_dict['usuaris'][u.username] = user_dict
    for uu in UnregisteredUser.objects.all():
        uu_dict = {'codi': u.codi}
        try:
            profile = Profile.objects.get(unregisteredUser=uu)
            uu_dict['alumne'] = profile.alumne.pk
        except Profile.DoesNotExist:
            uu_dict['alumne'] = None
        top_dict['uu'][uu.username] = uu_dict
    json.dump(top_dict, outfile, indent=None, separators=(',', ':'))

def optimize_pickle(nopkl, protocol=4):
    pkl = pickle.dumps(nopkl, protocol=protocol)
    return pickle.loads(pickletools.optimize(pkl))

def export_pickle(outfile, classe=None):
    info = PickledInfo()
    if classe is None:
        for c in Curs.objects.all():
            curs = PickledCurs.transform(c)
            for cl in Classe.objects.filter(curs=c):
                classe = PickledClasse.transform(cl)
                for a in Alumne.objects.filter(classe=cl):
                    alumne = PickledAlumne.transform(a)
                    classe.add_alumne(alumne)
                curs.add_classe(classe)
            info.add_curs(curs)
        for u in User.objects.all():
            info.add_user(PickledUser.transform(u))
        for uu in UnregisteredUser.objects.all():
            info.add_uu(PickledUnregisteredUser.transform(uu))
    else:
        info.add_curs(classe.curs)
        pcl = PickledClasse.transform(classe)
        for a in Alumne.objects.filter(classe=cl):
            alumne = PickledAlumne.transform(a)
            pcl.add_alumne(alumne)
    with gzip.GzipFile(fileobj=outfile) as gz:
        pickle.dump(optimize_pickle(info), gz, protocol=4)
