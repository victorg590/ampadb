from django.test import TestCase
from contactboard.models import *
from usermanager.models import *
from django.contrib.auth.models import User
from datetime import date
from .import_fmts import import_ampacsv, _importar_fila, InvalidFormat
from .pklf import PickledInfo, PickledAlumne
from . import ampacsv
from io import StringIO
import csv


class CsvImportTestCase(TestCase):
    def setUp(self):
        curs = Curs.objects.create(nom='Curs 1', id_interna='CURS1')
        classe = Classe.objects.create(nom='Test 1', id_interna='TEST1',
                                       curs=curs)

        alumne1 = Alumne.objects.create(
            pk=1, nom='A', cognoms='B', classe=classe,
            data_de_naixement=date(2000, 1, 1))
        usuari1 = User.objects.create(username='a')
        Profile.objects.create(alumne=alumne1, user=usuari1)

        alumne2 = Alumne.objects.create(
            pk=2, nom='C', cognoms='D', classe=classe,
            data_de_naixement=date(2000, 1, 1))
        usuari2 = UnregisteredUser.objects.create(username='b', codi='000000')
        Profile.objects.create(alumne=alumne2, unregisteredUser=usuari2)

        User.objects.create(username='c')
        UnregisteredUser.objects.create(username='d', codi='000000')

        alumne5 = Alumne.objects.create(
            pk=5, nom='O', cognoms='P', classe=classe
            data_de_naixement=date(2000, 1, 1))
        usuari5 = User.objects.create(username='e')
        Profile.objects.create(alumne=alumne5, user=usuari5)

    def test_user_already_exists(self):
        alumne = Alumne.objects.get(pk=1)
        self.assertEqual('A', alumne.nom)
        self.assertEqual('B', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        fila = {'pk': 1, 'Nom': 'Z', 'Cognoms': 'Y', 'Data de naixement':
                '2010-01-01'}
        _importar_fila(fila)
        alumne.refresh_from_db()
        self.assertEqual('Z', alumne.nom)
        self.assertEqual('Y', alumne.cognoms)
        self.assertEqual(date(2010, 1, 1), alumne.data_de_naixement)

    def test_user_unregistered(self):
        alumne = Alumne.objects.get(pk=2)
        self.assertEqual('C', alumne.nom)
        self.assertEqual('D', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        fila = {'pk': '2', 'Nom': 'X', 'Cognoms': 'W', 'Data de naixement':
                '2010-01-01'}
        _importar_fila(fila)
        alumne.refresh_from_db()
        self.assertEqual('X', alumne.nom)
        self.assertEqual('W', alumne.cognoms)
        self.assertEqual(date(2010, 1, 1), alumne.data_de_naixement)

    def test_associate_with_user(self):
        fila = {'Nom': 'E', 'Cognoms': 'F', 'Data de naixement': '2000-01-01',
                'Classe': 'TEST1', 'Usuari': 'c'}
        alumne = Alumne.objects.get(pk=int(_importar_fila(fila)['alumne']))
        self.assertEqual('E', alumne.nom)
        self.assertEqual('F', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST1', alumne.classe.id_interna)
        profile = Profile.objects.get(user=User.objects.get(username='c'))
        self.assertEqual(alumne, profile.alumne)

    def test_associate_with_unregistered_user(self):
        fila = {'Nom': 'G', 'Cognoms': 'H', 'Data de naixement': '2000-01-01',
                'Classe': 'TEST1', 'Usuari': 'd'}
        alumne = Alumne.objects.get(pk=int(_importar_fila(fila)['alumne']))
        self.assertEqual('G', alumne.nom)
        self.assertEqual('H', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST1', alumne.classe.id_interna)
        profile = Profile.objects.get(
            unregisteredUser=UnregisteredUser.objects.get(username='d'))
        self.assertEqual(alumne, profile.alumne)

    def test_new_user(self):
        fila = {'Nom': 'I', 'Cognoms': 'J', 'Data de naixement': '2000-01-01',
                'Classe': 'TEST1'}
        alumne = Alumne.objects.get(pk=int(_importar_fila(fila)['alumne']))
        self.assertEqual('I', alumne.nom)
        self.assertEqual('J', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST1', alumne.classe.id_interna)
        user = UnregisteredUser.objects.get(username='i.j')
        profile = Profile.objects.get(unregisteredUser=user)
        self.assertEqual(alumne, profile.alumne)

    def test_new_classe(self):
        fila = {'Nom': 'K', 'Cognoms': 'L', 'Data de naixement': '2000-01-01',
                'Classe': 'TEST2'}
        self.assertRaises(InvalidFormat, _importar_fila, fila)
        fila['Curs'] = 'CURS1'
        alumne = Alumne.objects.get(pk=int(_importar_fila(fila)['alumne']))
        self.assertEqual('K', alumne.nom)
        self.assertEqual('L', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST2', alumne.classe.id_interna)
        self.assertEqual('CURS1', alumne.classe.curs.id_interna)

    def test_new_curs(self):
        fila = {'Nom': 'M', 'Cognoms': 'N', 'Data de naixement': '2000-01-01',
                'Classe': 'TEST3'}
        self.assertRaises(InvalidFormat, _importar_fila, fila)
        fila['Curs'] = 'CURS2'
        alumne = Alumne.objects.get(pk=int(_importar_fila(fila)['alumne']))
        self.assertEqual('M', alumne.nom)
        self.assertEqual('N', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST3', alumne.classe.id_interna)
        self.assertEqual('CURS2', alumne.classe.curs.id_interna)

    def test_unchanged(self):
        fila = {'pk': '5'}
        alumne_orig = Alumne.objects.get(pk=5)
        alumne = Alumne.objects.get(pk=int(_importar_fila(fila)['alumne']))
        self.assertEqual(alumne_orig, alumne)
        profile = Profile.objects.get(alumne=alumne)
        self.assertEqual('e', profile.user.username)

    def test_delete_1(self):
        fila = {'pk': '1', 'Eliminar': '1'}
        self.assertEqual(_importar_fila(fila)['alumne'], None)
        self.assertRaises(Alumne.DoesNotExist, Alumne.objects.get, pk=1)

    def test_delete_2(self):
        fila = {'pk': '1', 'Eliminar': '2'}
        profile = Profile.objects.get(user=User.objects.get(username='a')).pk
        self.assertEqual(_importar_fila(fila)['alumne'], None)
        self.assertRaises(Alumne.DoesNotExist, Alumne.objects.get, pk=1)
        self.assertRaises(Profile.DoesNotExist, Profile.objects.get,
                          pk=profile)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='a')

    def test_delete_2_unregistered(self):
        fila = {'pk': '2', 'Eliminar': '2'}
        profile = Profile.objects.get(
            unregisteredUser=UnregisteredUser.objects.get(username='b')).pk
        self.assertEqual(_importar_fila(fila)['alumne'], None)
        self.assertRaises(Alumne.DoesNotExist, Alumne.objects.get, pk=2)
        self.assertRaises(Profile.DoesNotExist, Profile.objects.get,
                          pk=profile)
        self.assertRaises(UnregisteredUser.DoesNotExist,
                          UnregisteredUser.objects.get, username='a')

    def test_del_all(self):
        string = StringIO()
        ampacsv.get_template(string)
        writer = csv.DictWriter(string, ampacsv.FIELDNAMES)
        writer.writerow({'Nom': 'A', 'Cognoms': 'B', 'Classe': 'T1',
                         'Curs': 'T', 'Data de naixement': '2000-01-01'})
        string.seek(0)
        import_ampacsv(string, 'DEL_ALL')
        self.assertEqual(Alumne.objects.count(), 1)
        alumne = Alumne.objects.all()[0]
        self.assertEqual(alumne.nom, 'A')
        self.assertEqual(alumne.cognoms, 'B')

    def test_del(self):
        string = StringIO()
        ampacsv.get_template(string)
        writer = csv.DictWriter(string, ampacsv.FIELDNAMES)
        writer.writerow({'pk': '1', 'Nom': 'A', 'Cognoms': 'B',
                         'Data de naixement': '2000-01-01'})
        string.seek(0)
        import_ampacsv(string, 'DEL')
        self.assertEqual(Alumne.objects.count(), 1)
        alumne = Alumne.objects.all()[0]
        self.assertEqual(alumne.nom, 'A')
        self.assertEqual(alumne.cognoms, 'B')


class PickleImportTestCase(TestCase):
    @staticmethod
    def _get_def_val(key):
        if 'compartir_' in key:
            return False
        return ''

    def setUp(self):
        dict_test = {
            '_metadata': {'VERSION': 2},
            'cursos': [
                {
                    'id_interna': 'T',
                    'nom': 'T',
                    'ordre': 0,
                    'classes': [
                        {
                            'id_interna': 'T1',
                            'nom': '1',
                            'alumnes': [
                                {
                                    'pk': 1,
                                    'nom': 'A',
                                    'cognoms': 'B',
                                    'data_de_naixement': '2000-01-01'
                                }
                            ]
                        }
                    ]
                }
            ],
            'users': [], 'uu': [], 'grups_de_missatgeria': [],
            'extraescolars': [], 'conversacions': []}
        dict_test['cursos'][0]['classes'][0]['alumnes'][0].update(
            {k: self._get_def_val(k) for k in PickledAlumne.data if k not in
                dict_test['cursos'][0]['classes'][0]['alumnes'][0]})
        self.dict_test = dict_test

    def test_del_all(self):
        info = PickledInfo.from_json(self.dict_test)
        info.unpickle('DEL_ALL')
        self.assertEqual(Alumne.objects.count(), 1)
        alumne = Alumne.objects.all()[0]
        self.assertEqual(alumne.nom, 'A')
        self.assertEqual(alumne.cognoms, 'B')
