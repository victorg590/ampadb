from django.db import models
from django.urls import reverse
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
import re

# Veure https://es.wikipedia.org/wiki/Anexo:Prefijos_telef%C3%B3nicos_de_Espa%C3%B1a
telfRegex = re.compile(r'''
    ^
    ((\+|00)34)?  # Accepta prefixos (+34/0034)
    [679][0-9]{8}
    $
    ''', re.X)

class Alumne(models.Model):
    class Meta:
        ordering = ['cognoms', 'nom']

    nom = models.CharField(max_length=255, blank=False)
    cognoms = models.CharField(max_length=255, blank=False)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE)
    data_de_naixement = models.DateField(blank=False)
    nom_pare = models.CharField('nom del pare', max_length=255, blank=True)
    cognoms_pare = models.CharField('cognoms del pare', max_length=255,
        blank=True)
    nom_mare = models.CharField('nom de la mare', max_length=255, blank=True)
    cognoms_mare = models.CharField('cognoms de la mare', max_length=255,
        blank=True)
    correu_alumne = models.EmailField("correu de l'alumne", blank=True,
        validators=[validate_email])
    compartir_correu_alumne = models.BooleanField("compartir correu de"
        " l'alumne", default=False)
    correu_pare = models.EmailField("correu del pare", blank=True,
        validators=[validate_email])
    compartir_correu_pare = models.BooleanField("compartir correu del pare",
        default=False)
    correu_mare = models.EmailField("correu de la mare", blank=True,
        validators=[validate_email])
    compartir_correu_mare = models.BooleanField("compartir correu de la mare",
        default=False)
    telefon_alumne = models.CharField("telèfon de l'alumne", max_length=15,
        blank=True, validators=[RegexValidator(regex=telfRegex)])
    compartir_telefon_alumne = models.BooleanField("compartir telèfon de"
        " l'alumne", default=False)
    telefon_pare = models.CharField("telèfon del pare", max_length=15,
        blank=True, validators=[RegexValidator(regex=telfRegex)])
    compartir_telefon_pare = models.BooleanField("compartir telèfon del pare",
        default=False)
    telefon_mare = models.CharField("telèfon de la mare", max_length=15,
        blank=True, validators=[RegexValidator(regex=telfRegex)])
    compartir_telefon_mare = models.BooleanField("compartir telèfon de la mare",
        default=False)

    @property
    def compartir(self):
        fields = [self.compartir_correu_alumne, self.compartir_correu_pare,
            self.compartir_correu_mare, self.compartir_telefon_alumne,
            self.compartir_telefon_pare, self.compartir_telefon_mare]
        return all(fields)

    @compartir.setter
    def compartir(self, value):
        self.compartir_correu_alumne = value
        self.compartir_correu_pare = value
        self.compartir_correu_mare = value
        self.compartir_telefon_alumne = value
        self.compartir_telefon_pare = value
        self.compartir_telefon_mare = value

    def get_absolute_url(self):
        url = reverse('contactboard:edit-alumne', args=[self.pk])
        print(url)
        return url

    def __str__(self):
        return self.nom + ' ' + self.cognoms

    # Senyals associada: .signals.alumne_pre_save, .signals.alumne_pre_save

def validate_non_reserved_id(value):
    if value in ['admin', '-']:
        raise ValidationError('%(value)s is reserved for internal use',
            params={'value': value})

class Classe(models.Model):
    class Meta:
        ordering = ['curs', 'nom']

    nom = models.CharField(max_length=50, blank=False)
    id_interna = models.SlugField(max_length=20, primary_key=True,
        validators=[validate_non_reserved_id])
    curs = models.ForeignKey('Curs', on_delete=models.CASCADE,
        related_name='classes')

    def get_absolute_url(self):
        return reverse('contactboard:list', args=[self.id_interna])

    def __str__(self):
        return self.curs.nom + ' ' + self.nom

class Curs(models.Model):
    class Meta:
        verbose_name_plural = 'cursos'
        ordering = ['ordre', 'nom']
    nom = models.CharField(max_length=50, blank=False)
    id_interna = models.SlugField(max_length=20, primary_key=True)
    ordre = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.nom
