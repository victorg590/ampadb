from contactboard.models import *
from usermanager.models import *
from django.contrib.auth.models import User

def _def_list(*vals):
    """Torna `val` si no és None o un llista buida si ho és.
    Útil per a arguements opcionals. Admet diversos valors a la vegada.

    Si s'utilita opc=[], i la funció modifica opc, les següents trucades
    ja no començaràn amb una llista buida, sinó amb l'opc original.
    Veure http://pylint-messages.wikidot.com/messages:w0102
    """
    if len(vals) < 1:
        return
    elif len(vals) == 1:
        if vals[0] is None:
            return []
        return vals[0]
    else:
        ret = []
        for val in vals:
            if val is None:
                ret.append([])
            else:
                ret.append(val)
        return ret

class PickledAlumne:
    def __init__(self, pk, nom, cognoms, data_de_naixement, correu_alumne,
        correu_pare, correu_mare, telefon_pare, telefon_mare):
        self.pk = pk
        self.nom = nom
        self.cognoms = cognoms
        self.data_de_naixement = data_de_naixement
        self.correu_alumne = correu_alumne
        self.correu_pare = correu_pare
        self.correu_mare = correu_mare
        self.telefon_pare = telefon_pare
        self.telefon_mare = telefon_mare

    @classmethod
    def transform(cls, alumne):
        return cls(alumne.pk, alumne.nom, alumne.cognoms,
            alumne.data_de_naixement, alumne.correu_alumne, alumne.correu_pare,
            alumne.correu_mare, alumne.telefon_pare, alumne.telefon_mare)

    def unpickle(self, classe):
        try:
            alumne = Alumne.objects.get(pk=self.pk)
        except Alumne.DoesNotExist:
            alumne = Alumne(pk=self.pk)
        alumne.nom = self.nom
        alumne.cognoms = self.cognoms
        alumne.data_de_naixement = self.data_de_naixement
        alumne.correu_alumne = self.correu_alumne
        alumne.correu_pare = self.correu_pare
        alumne.correu_mare = self.correu_mare
        alumne.telefon_pare = self.telefon_pare
        alumne.telefon_mare = self.telefon_mare
        alumne.classe = Classe.objects.get(id_interna=classe.id_interna)
        alumne.save()
        return alumne

class PickledClasse:
    def __init__(self, id_interna, nom, alumnes=None):
        alumnes = _def_list(alumnes)
        self.id_interna = id_interna
        self.nom = nom
        self.alumnes = alumnes

    @classmethod
    def transform(cls, classe):
        return cls(classe.id_interna, classe.nom)

    def unpickle(self, curs):
        try:
            classe = Classe.objects.get(id_interna=self.id_interna)
        except Classe.DoesNotExist:
            classe = Classe(id_interna=self.id_interna)
        classe.nom = self.nom
        classe.curs = Curs.objects.get(id_interna=curs.id_interna)
        classe.save()
        return classe

    def add_alumne(self, alumne):
        self.alumnes.append(alumne)

class PickledCurs:
    def __init__(self, id_interna, nom, ordre, classes=None):
        classes = _def_list(classes)
        self.id_interna = id_interna
        self.nom = nom
        self.ordre = ordre
        self.classes = classes

    @classmethod
    def transform(cls, curs):
        return cls(curs.id_interna, curs.nom, curs.ordre)

    def unpickle(self):
        try:
            curs = Curs.objects.get(id_interna=self.id_interna)
        except Curs.DoesNotExist:
            curs = Curs(id_interna=self.id_interna)
        curs.nom = self.nom
        curs.ordre = self.ordre
        curs.save()
        return curs

    def add_classe(self, classe):
        self.classes.append(classe)

class PickledUser:
    def __init__(self, username, password, is_staff, is_superuser, alumne):
        self.username = username
        self.password = password
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.alumne = alumne

    @classmethod
    def transform(cls, user):
        try:
            profile = Profile.objects.get(user=user)
            alumne = profile.alumne.pk
        except Profile.DoesNotExist:
            alumne = None
        return cls(user.username, user.password, user.is_staff, user.
            is_superuser, alumne)

    def unpickle(self):
        try:
            user = User.objects.get(username=self.username)
        except User.DoesNotExist:
            user = User(username=self.username)
        user.password = self.password
        user.is_staff = self.is_staff
        user.is_superuser = self.is_superuser
        user.save()
        if self.alumne:
            alumne = Alumne.objects.get(pk=self.alumne)
            try:
                profile = Profile.objects.get(alumne=alumne)
            except Profile.DoesNotExist:
                profile = Profile(alumne=alumne)
            profile.user = user
            profile.save()
        return user

class PickledUnregisteredUser:
    def __init__(self, username, codi, alumne):
        self.username = username
        self.codi = codi
        self.alumne = alumne

    @classmethod
    def transform(cls, uu):
        try:
            profile = Profile.objects.get(unregisteredUser=uu)
            alumne = profile.alumne.pk
        except Profile.DoesNotExist:
            alumne = None
        return cls(uu.username, uu.codi, alumne)

    def unpickle(self):
        try:
            uu = UnregisteredUser.objects.get(username=self.username)
        except UnregisteredUser.DoesNotExist:
            uu = UnregisteredUser(username=self.username)
        uu.codi = self.codi
        uu.save()
        if self.alumne:
            alumne = Alumne.objects.get(pk=self.alumne)
            try:
                profile = Profile.objects.get(alumne=alumne)
            except Profile.DoesNotExist:
                profile = Profile(alumne=alumne)
            profile.unregisteredUser = uu
            profile.save()
        return uu

class PickledInfo:
    def __init__(self, cursos=None, users=None, uu=None):
        cursos, users, uu = _def_list(cursos, users, uu)
        self.VERSION = 1
        self.cursos = cursos
        self.users = users
        self.uu = uu

    def add_curs(self, curs):
        self.cursos.append(curs)

    def add_user(self, user):
        self.users.append(user)

    def add_uu(self, uuser):
        self.uu.append(uuser)
