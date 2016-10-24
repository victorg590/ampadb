from django.test import TestCase
from contactboard.models import *
from .models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date


class ProfileDeleteTestCase(TestCase):
    def setUp(self):
        curs = Curs.objects.create(id_interna='TEST', nom='TEST')
        classe = Classe.objects.create(id_interna='TEST', nom='T', curs=curs)

        alumne1 = Alumne.objects.create(
            pk=1, nom='A', cognoms='B', classe=classe,
            data_de_naixement=date(2000, 1, 1))
        user1 = User.objects.create(username='a.b')
        Profile.objects.update_or_create(alumne=alumne1,
                                         defaults={'user': user1})

        alumne2 = Alumne.objects.create(
            pk=2, nom='C', cognoms='D', classe=classe,
            data_de_naixement=date(2000, 1, 1))
        user2 = UnregisteredUser.objects.create(username='c.d', codi='000000')
        Profile.objects.update_or_create(alumne=alumne2,
                                         defaults={'unregisteredUser': user2})

        alumne3 = Alumne.objects.create(
            pk=3, nom='E', cognoms='F', classe=classe,
            data_de_naixement=date(2000, 1, 1))
        Profile.objects.update_or_create(alumne=alumne3)

    def test_with_user(self):
        alumne = Alumne.objects.get(pk=1)
        self.assertEqual('A', alumne.nom)
        self.assertEqual('B', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        profile = Profile.objects.get(alumne=alumne)
        profile_pk = profile.pk
        user = User.objects.get(username='a.b')
        self.assertEqual(user, profile.user)
        self.assertEqual(None, profile.unregisteredUser)
        del profile, user
        alumne.delete()
        self.assertRaises(Profile.DoesNotExist, Profile.objects.get,
                          pk=profile_pk)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='a.b')

    def test_with_unregistered_user(self):
        alumne = Alumne.objects.get(pk=2)
        self.assertEqual('C', alumne.nom)
        self.assertEqual('D', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        profile = Profile.objects.get(alumne=alumne)
        profile_pk = profile.pk
        user = UnregisteredUser.objects.get(username='c.d')
        self.assertEqual(None, profile.user)
        self.assertEqual(user, profile.unregisteredUser)
        del profile, user
        alumne.delete()
        self.assertRaises(Profile.DoesNotExist, Profile.objects.get,
                          pk=profile_pk)
        self.assertRaises(UnregisteredUser.DoesNotExist,
                          UnregisteredUser.objects.get, username='c.d')

    def test_with_no_user(self):
        alumne = Alumne.objects.get(pk=3)
        self.assertEqual('E', alumne.nom)
        self.assertEqual('F', alumne.cognoms)
        self.assertEqual(date(2000, 1, 1), alumne.data_de_naixement)
        profile = Profile.objects.get(alumne=alumne)
        profile_pk = profile.pk
        self.assertEqual(None, profile.user)
        self.assertEqual(None, profile.unregisteredUser)
        alumne.delete()
        del profile
        self.assertRaises(Profile.DoesNotExist, Profile.objects.get,
                          pk=profile_pk)


class ProfileTestCase(TestCase):
    def setUp(self):
        curs = Curs.objects.create(id_interna='TEST', nom='TEST')
        classe = Classe.objects.create(id_interna='TEST', nom='T', curs=curs)

        self.alumne = Alumne.objects.create(
            pk=1, nom='A', cognoms='B', classe=classe,
            data_de_naixement=date(2000, 1, 1))

    def test_not_both_users(self):
        profile = Profile(alumne=self.alumne)
        user = User.objects.create(username='a.b_a')
        profile.user = user
        unregisteredUser = UnregisteredUser.objects.create(username='a.b_b',
                                                           codi='000000')
        profile.unregisteredUser = unregisteredUser
        self.assertRaises(ValidationError, profile.save)


class UnregisteredUserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='a.b')

    def test_no_repeated_username(self):
        self.assertRaises(ValidationError, UnregisteredUser.objects.create,
                          username='a.b')

    def test_invalid_username(self):
        invalid_names = ['', 'á', 'ñ', 'ç', '_', '!', '$', '?',
                         ''.join('x' for _ in range(31))]
        for n in invalid_names:
            try:
                UnregisteredUser.objects.create(username=n)
            except ValidationError:
                pass
            else:
                self.fail("'%s' es reconeix com a un nom d'usuari vàlid" % n)
