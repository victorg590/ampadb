from django.db import models
from django.contrib.auth.models import User
from contactboard.models import Alumne
from django.core import validators
from django.core.exceptions import ValidationError

class Profile(models.Model):
    class Meta:
        verbose_name = 'perfil'
    user = models.OneToOneField(User, verbose_name='usuari', blank=True,
        null=True, on_delete=models.SET_NULL)
    unregisteredUser = models.OneToOneField('UnregisteredUser',
        verbose_name='usuari (no registrat)',
        blank=True, null=True, on_delete=models.SET_NULL)
    alumne = models.OneToOneField(Alumne, primary_key=True,
        on_delete=models.CASCADE)

    @classmethod
    def cleanup(cls):
        """Elimina tots els registres sense `user` ni `unregisteredUser`"""
        return cls.objects.filter(user__isnull=True,
            unregisteredUser__isnull=True).delete()

    def clean(self):
        super().clean()
        if self.user and self.unregisteredUser:
            raise ValidationError("Només es pot definir un de: `user` i"
                " `unregisteredUser`")

    def __str__(self):
        return str(self.alumne)

    # Senyal associada: .signals.profile_pre_delete

def validate_username_unique(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError('Username exists!')

def validate_alumne_unique(value):
    if Profile.objects.filter(alumne=value).exists():
        raise ValidationError('Alumne already has a user associated!')

class UnregisteredUser(models.Model):
    class Meta:
        verbose_name = 'usuari no registrat'
        verbose_name_plural = 'usuaris no registrats'
    username = models.CharField("nom d'usuari", max_length=30, primary_key=True,
        validators=[
            validators.RegexValidator(r'^[\w.@+-]{1,30}$'),
            validate_username_unique
        ])
    # El codi és d'un sol ús, pel que, a diferència de la contrasenya,
    # no és necessari protegir-lo amb un hash
    codi = models.CharField(max_length=6, blank=False,
        validators=[validators.RegexValidator(r'^[0-9]{6}$')],
        help_text="Un codi numèric de 6 dígits per confirmar que l'usuari "
            "pertany a aquesta persona. Si no s'entra cap, es generarà un "
            "automàticament")

    def clean(self):
        super().clean()
        if User.objects.filter(username=self.username).exists():
            self.add_error('username',
                ValidationError("Aquest nom d'usuari ja exiteix i està"
                " registrat"))

    def __str__(self):
        return self.username + ' (*)'
