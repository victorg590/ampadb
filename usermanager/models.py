from django.db import models
from django.contrib.auth.models import User
from contactboard.models import Alumne
from django.core import validators
from django.core.exceptions import ValidationError

class Profile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name='Usuari')
    unregisteredUser = models.OneToOneField('unregisteredUser', blank=True,
        null=True, on_delete=models.SET_NULL,
        verbose_name='Usuari (sense registrar)')
    alumne = models.OneToOneField(Alumne, primary_key=False,
        on_delete=models.CASCADE)

    def __str__(self):
        return str(self.alumne)

def validate_username_unique(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError('Username exists!')

def validate_alumne_unique(value):
    if Profile.objects.filter(alumne=value).exists():
        raise ValidationError('Alumne already has a user associated!')

class UnregisteredUser(models.Model):
    username = models.CharField(max_length=30, primary_key=True, validators=[
        validators.RegexValidator(r'^[\w.@+-]+$'),
        validate_username_unique
    ], verbose_name="Nom d'usuari")
    # El codi és d'un sol ús, pel que, a diferència de la contrasenya,
    # no és necessari protegir-lo amb un hash
    codi = models.CharField(max_length=6, blank=False,
        validators=[validators.RegexValidator(r'^[0-9]{6}$')],
        help_text="Un codi numèric de 6 dígits per confirmar que l'usuari "
            "pertany a aquesta persona. Si no s'entra cap, es generarà un "
            "automàticament")

    def __str__(self):
        return self.username + ' (*)'
