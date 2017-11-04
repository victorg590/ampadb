import re
from django.db import models
from django.urls import reverse
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError

# Veure
# https://es.wikipedia.org/wiki/Anexo:Prefijos_telef%C3%B3nicos_de_Espa%C3%B1a
TELF_REGEX = re.compile(r'''
    ^
    ((\+|00)34)?  # Accepta prefixos (+34/0034)
    [679][0-9]{8}
    $
    ''', re.VERBOSE)


class Alumne(models.Model):
    class Meta:
        ordering = ['cognoms', 'nom']
        unique_together = ('nom', 'cognoms')

    nom = models.CharField(max_length=255, blank=False)
    cognoms = models.CharField(max_length=255, blank=False)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE)
    nom_tutor_1 = models.CharField(
        'nom del tutor 1', max_length=255, blank=True)
    cognoms_tutor_1 = models.CharField(
        'cognoms del tutor 1', max_length=255, blank=True)
    nom_tutor_2 = models.CharField(
        'nom del tutor 2', max_length=255, blank=True)
    cognoms_tutor_2 = models.CharField(
        'cognoms del tutor 2', max_length=255, blank=True)
    correu_alumne = models.EmailField(
        "correu de l'alumne", blank=True, validators=[validate_email])
    compartir_correu_alumne = models.BooleanField(
        "compartir correu de l'alumne", default=False)
    correu_tutor_1 = models.EmailField(
        "correu del tutor 1", blank=True, validators=[validate_email])
    compartir_correu_tutor_1 = models.BooleanField(
        "compartir correu del tutor 1", default=False)
    correu_tutor_2 = models.EmailField(
        "correu del tutor 2", blank=True, validators=[validate_email])
    compartir_correu_tutor_2 = models.BooleanField(
        "compartir correu del tutor 2", default=False)
    telefon_alumne = models.CharField(
        "telèfon de l'alumne",
        max_length=15,
        blank=True,
        validators=[RegexValidator(regex=TELF_REGEX)])
    compartir_telefon_alumne = models.BooleanField(
        "compartir telèfon de l'alumne", default=False)
    telefon_tutor_1 = models.CharField(
        "telèfon del tutor 1",
        max_length=15,
        blank=True,
        validators=[RegexValidator(regex=TELF_REGEX)])
    compartir_telefon_tutor_1 = models.BooleanField(
        "compartir telèfon del tutor 1", default=False)
    telefon_tutor_2 = models.CharField(
        "telèfon del tutor 2",
        max_length=15,
        blank=True,
        validators=[RegexValidator(regex=TELF_REGEX)])
    compartir_telefon_tutor_2 = models.BooleanField(
        "compartir telèfon del tutor 2", default=False)

    def get_absolute_url(self):
        url = reverse('contactboard:edit-alumne', args=[self.pk])
        return url

    def __str__(self):
        return self.nom + ' ' + self.cognoms

    # Senyals associada: .signals.alumne_pre_save, .signals.alumne_pre_save


def validate_non_reserved_id(value):
    if value in ['admin', '-']:
        raise ValidationError(
            '%(value)s is reserved for internal use', params={
                'value': value
            })


class Classe(models.Model):
    class Meta:
        ordering = ['curs', 'nom']

    nom = models.CharField(max_length=50, blank=False)
    id_interna = models.SlugField(
        max_length=20, primary_key=True, validators=[validate_non_reserved_id])
    curs = models.ForeignKey(
        'Curs', on_delete=models.CASCADE, related_name='classes')

    def get_absolute_url(self):
        return reverse('contactboard:list', args=[self.id_interna])

    def __str__(self):
        return self.curs.nom + ' ' + self.nom  # pylint: disable=no-member


class Curs(models.Model):
    class Meta:
        verbose_name_plural = 'cursos'
        ordering = ['ordre', 'nom']

    nom = models.CharField(max_length=50, blank=False)
    id_interna = models.SlugField(max_length=20, primary_key=True)
    ordre = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.nom
