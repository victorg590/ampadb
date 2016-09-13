from contactboard.models import *
from usermanager.models import *
from extraescolars.models import *
from missatges.models import *
from django.contrib.auth.models import User
from decimal import Decimal
import datetime

CURRENT_VERSION = 2

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

DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M:%S.%f%z'

class PickledAlumne:
    data = ('nom', 'cognoms', 'data_de_naixement', 'nom_pare', 'cognoms_pare',
        'nom_mare', 'cognoms_mare', 'correu_alumne', 'compartir_correu_alumne',
        'correu_pare', 'compartir_correu_pare', 'correu_mare',
        'compartir_correu_mare', 'telefon_alumne', 'compartir_telefon_alumne',
        'telefon_pare', 'compartir_telefon_pare', 'telefon_mare',
        'compartir_telefon_mare')
    def __init__(self, *, pk, **kwargs):
        self.pk = pk  # PK és un cas especial
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, alumne):
        kwargs = {k: getattr(alumne, k) for k in cls.data}
        return cls(pk=alumne.pk, **kwargs)

    def unpickle(self, classe):
        return Alumne.objects.update_or_create(pk=self.pk,
            defaults={'classe': classe}.update(
            {k: getattr(self, k) for k in self.data}))[0]

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data
            if k != 'data_de_naixement'}
        dest['pk'] = self.pk
        dest['data_de_naixement'] = self.data_de_naixement.strftime(DATE_FMT)
        return dest

    @classmethod
    def from_json(cls, orig):
        corig = {k: v for k, v in orig.items() if k != 'data_de_naixement'}
        corig['data_de_naixement'] = datetime.date.strptime(
            orig['data_de_naixement'], DATE_FMT)
        return cls(data_de_naixement=date.date.strptime(
            orig['data_de_naixement'], DATE_FMT), **corig)

class PickledClasse:
    data = ('nom',)
    def __init__(self, *, id_interna, alumnes=None, **kwargs):
        self.id_interna = id_interna
        self.alumnes = _def_list(alumnes)
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, classe, recursive=True):
        kwargs = {k: getattr(classe, k) for k in cls.data}
        if recursive:
            alumnes = [PickledAlumne.transform(a)
                for a in Alumne.objects.filter(classe=classe)]
        return cls(id_interna=classe.id_interna, alumnes=alumnes, **kwargs)

    def unpickle(self, curs):
        classe = Classe.objects.update_or_create(id_interna=self.id_interna,
            defaults={'curs': curs}.update(
            {k: getattr(self, k) for k in self.data}))[0]
        for a in self.alumnes:
            a.unpickle(classe)
        return classe

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data}
        dest['id_interna'] = self.id_interna
        dest['alumnes'] = [a.to_json() for a in self.alumnes]
        return dest

    @classmethod
    def from_json(cls, orig):
        corig = {k: v for k, v in orig.items() if k != 'alumnes'}
        return cls(
            alumnes=[PickledAlumne.from_json(a) for a in orig['alumnes']],
            **corig)

class PickledCurs:
    data = ('nom', 'ordre')
    def __init__(self, *, id_interna, classes=None, **kwargs):
        self.id_interna = id_interna
        self.classes = _def_list(classes)
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, curs, recursive=True):
        kwargs = {k: getattr(curs, k) for k in cls.data}
        if recursive:
            classes = [PickledClasse.transform(c)
                for c in Classe.objects.filter(curs=curs)]
        return cls(id_interna=curs.id_interna, classes=classes, **kwargs)

    def unpickle(self):
        try:
            curs = Curs.objects.get(id_interna=self.id_interna)
        except Curs.DoesNotExist:
            curs = Curs(id_interna=self.id_interna)
        curs = Curs.objects.update_or_create(id_interna=self.id_interna,
            defaults={k: getattr(self, k) for k in self.data})[0]
        for c in self.classes:
            c.unpickle(curs)
        return curs

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data}
        dest['id_interna'] = self.id_interna
        dest['classes'] = [c.to_json() for c in self.classes]
        return dest

    @classmethod
    def from_json(cls, orig):
        corig = {k: v for k, v in orig.items() if k != 'classes'}
        return cls(
            classes=[PickledClasse.from_json(c) for c in orig['classes']],
            **corig)

class PickledUser:
    data = ('password', 'is_staff', 'is_superuser')
    def __init__(self, *, username, alumne=None, **kwargs):
        self.username = username
        self.alumne = alumne
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, user):
        try:
            profile = Profile.objects.get(user=user)
            alumne = profile.alumne.pk
        except Profile.DoesNotExist:
            alumne = None
        kwargs = {k: getattr(user, k) for k in cls.data}
        return cls(username=user.username, alumne=alumne, **kwargs)

    def unpickle(self):
        try:
            user = User.objects.get(username=self.username)
        except User.DoesNotExist:
            user = User(username=self.username)
        user = User.update_or_create(username=self.username,
            defaults={k: getattr(self, k) for k in self.data})[0]
        if self.alumne:
            Profile.objects.update_or_create(alumne=Alumne.objects.get(
                pk=alumne), defaults={'user': user, 'unregisteredUser': None})
        return user

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data}
        dest['username'] = self.username
        dest['alumne'] = self.alumne
        return dest

    @classmethod
    def from_json(cls, orig):
        return cls(**orig)

class PickledUnregisteredUser:
    data = ('codi',)
    def __init__(self, *, username, alumne=None, **kwargs):
        self.username = username
        self.alumne = alumne
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, uu):
        try:
            profile = Profile.objects.get(unregisteredUser=uu)
            alumne = profile.alumne.pk
        except Profile.DoesNotExist:
            alumne = None
        kwargs = {k: getattr(uu, k) for k in cls.data}
        return cls(username=uu.username, alumne=alumne, **kwargs)

    def unpickle(self):
        try:
            uu = UnregisteredUser.objects.get(username=self.username)
        except UnregisteredUser.DoesNotExist:
            uu = UnregisteredUser(username=self.username)
        uu = UnregisteredUser.objects.update_or_create(username=self.username,
            defaults={k: getattr(self, k) for k in self.data})[0]
        if self.alumne:
            Profile.objects.update_or_create(alumne=Alumne.objects.get(
                pk=self.alumne), defaults={'user': None,
                'unregisteredUser': uu})
        return uu

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data}
        dest['username'] = self.username
        dest['alumne'] = self.alumne
        return dest

    @classmethod
    def from_json(cls, orig):
        return cls(**orig)

class PickledInscripcio:
    data = ('confirmat', 'pagat')
    def __init__(self, *, alumne, **kwargs):
        self.alumne = alumne
        for k in self.data:
            setattr(self, k, kwargs[k])

    @classmethod
    def transform(cls, inscripcio):
        kwargs = {k: getattr(inscripcio, k) for k in cls.data}
        return cls(alumne=inscripcio.alumne.pk, **kwargs)

    def unpickle(self, activitat):
        return Inscripcio.objects.update_or_create(activitat=activitat,
            alumne=Alumne.objects.get(pk=self.alumne),
            defaults={k: getattr(self, k) for k in self.data})[0]

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data}
        dest['alumne'] = self.alumne
        return dest

    @classmethod
    def from_json(self, orig):
        return cls(**orig)

class PickledExtraescolar:
    data = ('nom', 'descripcio_curta', 'inscripcio_des_de', 'inscripcio_fins_a',
        'preu')
    def __init__(self, *, id_interna, cursos=None, inscripcions=None, **kwargs):
        self.cursos, self.inscripcions = _def_list(cursos, inscripcions)
        self.id_interna = id_interna
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, ext):
        kwargs = {k: getattr(ext, k) for k in cls.data}
        return cls(id_interna=ext.id_interna,
            cursos=[c.pk for c in ext.cursos.all()],
            inscripcions=[PickledInscripcio.transform(i) for i in
                Inscripcio.objects.filter(activitat=ext)], **kwargs)

    def unpickle(self):
        obj = Extraescolar.objects.update_or_create(id_interna=self.id_interna,
            defaults={k: getattr(self, k) for k in self.data})[0]
        for c in self.cursos:
            obj.cursos.add(Curs.objects.get(pk=c))
        for i in self.inscripcions:
            i.unpickle(obj)
        return obj

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data if k not in ['preu',
            'inscripcio_des_de', 'inscripcio_fins_a']}
        dest['cursos'] = self.cursos
        dest['inscripcions'] = [i.to_json() for i in self.inscripcions]
        dest['preu'] = float(self.preu)
        if self.inscripcio_des_de is not None:
            dest['inscripcio_des_de'] = self.inscripcio_des_de.strftime(
                DATE_FMT)
        else:
            dest['inscripcio_des_de'] = None
        if self.inscripcio_fins_a is not None:
            dest['inscripcio_fins_a'] = self.inscripcio_fins_a.strftime(
                DATE_FMT)
        else:
            dest['inscripcio_fins_a'] = None
        return dest

    @classmethod
    def from_json(cls, orig):
        corig = {k: v for k, v in orig.items() if k not in ['inscripcions',
            'preu', 'inscripcio_des_de', 'inscripcio_fins_a']}
        if orig['inscripcio_des_de'] is not None:
            corig['inscripcio_des_de'] = datetime.datetime.strptime(
                orig['inscripcio_des_de'], DATE_FMT)
        else:
            corig['inscripcio_des_de'] = None
        if orig['inscripcio_des_de'] is not None:
            corig['inscripcio_fins_a'] = datetime.datetime.strptime(
                orig['inscripcio_fins_a'], DATE_FMT)
        else:
            corig['inscripcio_fins_a'] = None
        return cls(
            inscripcions=[PickledInscripcio.from_json(i) for i in
                orig['inscripcions']],
            preu=Decimal(str(orig['preu'])),
            **corig)

class PickledGrupDeMissatgeria:
    data = ('nom', 'motius')
    def __init__(self, *, pk, usuaris=None, **kwargs):
        self.pk = pk
        self.usuaris = _def_list(usuaris)
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, gdm):
        kwargs = {k: getattr(gdm, k) for k in cls.data}
        return cls(pk=gdm.pk, usuaris=[u.username for u in gdm.usuaris.all()],
            **kwargs)

    def unpickle(self):
        obj = Extraescolar.objects.update_or_create(pk=self.pk,
            defaults={k: getattr(self, k) for k in self.data})[0]
        usuaris = [User.objects.get(username=u) for u in self.usuaris]
        obj.usuaris.add(*usuaris)
        return obj

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data}
        dest['pk'] = self.pk
        dest['usuaris'] = self.usuaris
        return dest

    @classmethod
    def from_json(cls, orig):
        return cls(**orig)

class PickledMissatge:
    data = ('contingut', 'enviat', 'editat', 'estat')
    def __init__(self, *, per, ordre, **kwargs):
        self.per = per
        self.ordre = ordre
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, msg):
        kwargs = {k: getattr(msg, k) for k in cls.data}
        return cls(per=msg.per.username, ordre=msg.ordre, **kwargs)

    def unpickle(self, conversacio):
        msg = Missatge.objects.update_or_create(conversacio=conversacio,
            ordre=self.ordre, default={
            'per': User.objects.get(username=self.per)}.update(
            {k: getattr(self, k) for k in self.data}))[0]
        msg.calcular_destinataris(True)
        return msg

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data if k not in ['enviat',
            'editat']}
        dest['per'] = self.per
        dest['ordre'] = self.ordre
        dest['enviat'] = self.enviat.strftime(DATETIME_FMT)
        dest['editat'] = self.editat.strftime(DATETIME_FMT)
        return dest

    @classmethod
    def from_json(cls, orig):
        corig = {k: v for k, v in orig.items() if k not in ['enviat', 'editat']}
        return cls(
            enviat=datetime.datetime.strptime(orig['enviat'], DATETIME_FMT),
            editat=datetime.datetime.strptime(orig['editat'], DATETIME_FMT),
            **corig)

class PickledConversacio:
    data = ('assumpte', 'tancat')
    def __init__(self, *, pk, de, a, missatges=None, **kwargs):
        self.pk = pk
        self.de = de
        self.a = a
        self.missatges = _def_list(missatges)
        for d in self.data:
            setattr(self, d, kwargs[d])

    @classmethod
    def transform(cls, conv):
        kwargs = {k: getattr(conv, k) for k in cls.data}
        return cls(pk=conv.pk, de=conv.de.pk, a=conv.a.pk,
            missatges=[PickledMissatge.transform(m) for m in
            Missatge.objects.filter(conversacio=conv)], **kwargs)

    def unpickle(self):
        obj = Conversacio.objects.update_or_create(pk=self.pk,
            default={'de': User.objects.get(pk=self.de),
            'a': GrupDeMissatgeria.objects.get(pk=self.a)}.update(
            {k: getattr(self, k) for k in self.data}))
        for m in self.missatges:
            m.unpickle(obj)
        return obj

    def to_json(self):
        dest = {k: getattr(self, k) for k in self.data}
        dest['pk'] = self.pk
        dest['de'] = self.de
        dest['a'] = self.a
        dest['missatges'] = [m.to_json() for m in self.missatges]
        return dest

    @classmethod
    def from_json(cls, orig):
        corig = {k: v for k, v in orig.items() if k != 'missatges'}
        return cls(
        missatges=[PickledMissatge.from_json(m) for m in orig['missatges']],
        **corig)

class PickledInfo:
    def check_version(self, expected):
        if expected != self.VERSION:
            raise ValueError('La versió del nou document no és compatible'
                ' amb aquesta versió')

    def __init__(self, cursos=None, users=None, uu=None,
        grups_de_missatgeria=None, extraescolars=None, conversacions=None, *,
        VERSION=None):
        self.VERSION = CURRENT_VERSION
        if VERSION:
            self.check_version(VERSION)
        (self.cursos, self.users, self.uu, self.grups_de_missatgeria,
        self.extraescolars, self.conversacions) = _def_list(cursos, users,
                uu, grups_de_missatgeria, extraescolars, conversacions)
        self.cursos = cursos
        self.users = users
        self.uu = uu
        self.grups_de_missatgeria = grups_de_missatgeria
        self.extraescolars = extraescolars
        self.conversacions = conversacions

    @classmethod
    def transform(cls):
        cursos = []
        for c in Curs.objects.all():
            cursos.append(PickledCurs.transform(c))
        users = []
        for u in User.objects.all():
            users.append(PickledUser.transform(u))
        uu = []
        for u in UnregisteredUser.objects.all():
            uu.append(PickledUnregisteredUser.transform(u))
        grups_de_missatgeria = []
        for gdm in GrupDeMissatgeria.objects.all():
            grups_de_missatgeria.append(PickledGrupDeMissatgeria.transform(gdm))
        extraescolars = []
        for act in Extraescolar.objects.all():
            extraescolars.append(PickledExtraescolar.transform(act))
        conversacions = []
        for conv in Conversacio.objects.all():
            conversacions.append(PickledConversacio.transform(conv))
        return cls(cursos, users, uu, grups_de_missatgeria, extraescolars,
            conversacions)

    def unpickle(self):
        for c in self.cursos:
            c.unpickle()
        for u in self.users:
            u.unpickle()
        for u in self.uu:
            u.unpickle()
        for gdm in self.grups_de_missatgeria:
            gdm.unpickle()
        for act in self.extraescolars:
            act.unpickle()
        for conv in self.conversacions:
            conv.unpickle()

    def to_json(self):
        dest = {'_metadata': {}}
        dest['_metadata']['VERSION'] = self.VERSION
        dest['cursos'] = [c.to_json() for c in self.cursos]
        dest['users'] = [u.to_json() for u in self.users]
        dest['uu'] = [u.to_json() for u in self.uu]
        dest['grups_de_missatgeria'] = [gdm.to_json() for gdm in
            self.grups_de_missatgeria]
        dest['extraescolars'] = [act.to_json() for act in self.extraescolars]
        dest['conversacions'] = [conv.to_json() for conv in self.conversacions]
        return dest

    @classmethod
    def from_json(cls, orig):
        return cls(
            VERSION=orig['_metadata']['VERSION'],
            cursos=[PickledCurs.from_json(c) for c in orig['cursos']],
            users=[PickledUser.from_json(u) for u in orig['users']],
            uu=[PickledUnregisteredUser.from_json(u) for u in orig['uu']],
            grups_de_missatgeria=[PickledGrupDeMissatgeria.from_json(gdm)
                for gdm in orig['grups_de_missatgeria']],
            extraescolars=[PickledExtraescolar.from_json(act) for act in orig[
                'extraescolars']],
            conversacions=[PickledConversacio.from_json(conv) for conv in orig[
                'conversacions']]
        )
