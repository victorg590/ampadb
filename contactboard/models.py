from django.db import models
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
import re

# Create your models here.

# Veure https://es.wikipedia.org/wiki/Anexo:Prefijos_telef%C3%B3nicos_de_Espa%C3%B1a
telfRegex = re.compile(r'''
    ((\+|00)34)?  # Accepta prefixos (+34/0034)
    [679][0-9]{8}
    ''', re.X)

class Alumne(models.Model):
    nom = models.CharField(max_length=255, blank=False)
    cognoms = models.CharField(max_length=255, blank=False)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE)
    data_de_naixement = models.DateField(blank=False)
    correu_alumne = models.EmailField(blank=True, validators=[validate_email])
    correu_pare = models.EmailField(blank=True, validators=[validate_email])
    correu_mare = models.EmailField(blank=True, validators=[validate_email])
    telefon_pare = models.CharField(max_length=15, blank=True,
        validators=[RegexValidator(regex=telfRegex)],
        verbose_name='telèfon pare')
    telefon_mare = models.CharField(max_length=15, blank=True,
        validators=[RegexValidator(regex=telfRegex)],
        verbose_name='telèfon mare')
    compartir = models.BooleanField(default=False)

    def __str__(self):
        return self.nom + ' ' + self.cognoms

class Curs(models.Model):
    nom = models.CharField(max_length=50, blank=False)
    id_interna = models.SlugField(max_length=20, primary_key=True)
    ordre = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.nom

def validate_valid_id(value):
    if value in ['admin', '-']:
        raise ValidationError('%(value)s is reserved for internal use',
            params={'value': value})

class Classe(models.Model):
    nom = models.CharField(max_length=50, blank=False)
    id_interna = models.SlugField(max_length=20, primary_key=True,
        validators=[validate_valid_id])
    curs = models.ForeignKey(Curs, on_delete=models.CASCADE, related_name='classes')

    def __str__(self):
        return self.curs.nom + ' ' + self.nom
