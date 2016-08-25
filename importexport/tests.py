from django.test import TestCase
from contactboard.models import *
from usermanager.models import *
from django.contrib.auth.models import User
from datetime import date
from .import_fmts import _importar_fila, InvalidFormat

# Create your tests here.
class CsvImportTestCase(TestCase):
    def setUp(self):
        curs = Curs.objects.create(nom='Curs 1', id_interna='CURS1')
        classe = Classe.objects.create(nom='Test 1', id_interna='TEST1',
            curs=curs)

        alumne1 = Alumne.objects.create(pk=1, nom='A', cognoms='B',
            data_de_naixement=date(2000, 1, 1), classe=classe)
        usuari1 = User.objects.create(username='1')
        Profile.objects.create(alumne=alumne1, user=usuari1)

        alumne2 = Alumne.objects.create(pk=2, nom='C', cognoms='D',
            data_de_naixement=date(2000, 1, 1), classe=classe)
        usuari2 = UnregisteredUser.objects.create(username='2', codi='000000')
        Profile.objects.create(alumne=alumne2, unregisteredUser=usuari2)

        User.objects.create(username='3')
        UnregisteredUser.objects.create(username='4', codi='000000')

        alumne5 = Alumne.objects.create(pk=5, nom='O', cognoms='P',
            data_de_naixement=date(2000, 1, 1), classe=classe)
        usuari5 = User.objects.create(username='5')
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
            'Classe': 'TEST1', 'Usuari': '3'}
        alumne = Alumne.objects.get(pk=_importar_fila(fila))
        self.assertEqual('E', alumne.nom)
        self.assertEqual('F', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST1', alumne.classe.id_interna)
        profile = Profile.objects.get(user=User.objects.get(username='3'))
        self.assertEqual(alumne, profile.alumne)

    def test_associate_with_unregistered_user(self):
        fila = {'Nom': 'G', 'Cognoms': 'H', 'Data de naixement': '2000-01-01',
            'Classe': 'TEST1', 'Usuari': '4'}
        alumne = Alumne.objects.get(pk=_importar_fila(fila))
        self.assertEqual('G', alumne.nom)
        self.assertEqual('H', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST1', alumne.classe.id_interna)
        profile = Profile.objects.get(
            unregisteredUser=UnregisteredUser.objects.get(username='4'))
        self.assertEqual(alumne, profile.alumne)

    def test_new_user(self):
        fila = {'Nom': 'I', 'Cognoms': 'J', 'Data de naixement': '2000-01-01',
            'Classe': 'TEST1'}
        alumne = Alumne.objects.get(pk=_importar_fila(fila))
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
        alumne = Alumne.objects.get(pk=_importar_fila(fila))
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
        alumne = Alumne.objects.get(pk=_importar_fila(fila))
        self.assertEqual('M', alumne.nom)
        self.assertEqual('N', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        self.assertEqual('TEST3', alumne.classe.id_interna)
        self.assertEqual('CURS2', alumne.classe.curs.id_interna)

    def test_unchanged(self):
        fila = {'pk': '5'}
        alumne_orig = Alumne.objects.get(pk=5)
        alumne = Alumne.objects.get(pk=_importar_fila(fila))
        self.assertEqual(alumne_orig, alumne)
        profile = Profile.objects.get(alumne=alumne)
        self.assertEqual('5', profile.user.username)

    def test_delete_1(self):
        fila = {'pk': '1', 'Eliminar': '1'}
        self.assertEqual(_importar_fila(fila), None)
        self.assertRaises(Alumne.DoesNotExist, Alumne.objects.get, pk=1)

    def test_delete_2(self):
        fila = {'pk': '1', 'Eliminar': '2'}
        profile = Profile.objects.get(user=User.objects.get(username='1')).pk
        self.assertEqual(_importar_fila(fila), None)
        self.assertRaises(Alumne.DoesNotExist, Alumne.objects.get, pk=1)
        self.assertRaises(Profile.DoesNotExist, Profile.objects.get, pk=profile)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='1')

    def test_delete_2_unregistered(self):
        fila = {'pk': '2', 'Eliminar': '2'}
        profile = Profile.objects.get(
            unregisteredUser=UnregisteredUser.objects.get(username='2')).pk
        self.assertEqual(_importar_fila(fila), None)
        self.assertRaises(Alumne.DoesNotExist, Alumne.objects.get, pk=2)
        self.assertRaises(Profile.DoesNotExist, Profile.objects.get, pk=profile)
        self.assertRaises(UnregisteredUser.DoesNotExist,
            UnregisteredUser.objects.get, username='1')
