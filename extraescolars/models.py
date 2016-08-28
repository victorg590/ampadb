from django.db import models
from django.core import validators
from django.urls import reverse
from contactboard.models import Curs, Alumne
from decimal import Decimal

_text_md = 'Suporta <a href="https://ca.wikipedia.org/wiki/Markdown">Markdown</a>'

class Extraescolar(models.Model):
    nom = models.CharField(blank=False, null=False, max_length=50)
    id_interna = models.SlugField(primary_key=True, max_length=20)
    descripcio_curta = models.CharField('Descripció curta', blank=True,
        max_length=80,
        help_text="Una descripció curta per mostrar a la llista "
            "d'extraescolars. Máxim 80 caracters.")
    descripcio = models.TextField('Descripció', blank=True,
        help_text=_text_md)
    horari = models.TextField(blank=True, help_text=_text_md)
    inscripcio_des_de = models.DateTimeField('Inscripció des de', blank=True,
        null=True, help_text="Des de quan es permet la "
            "inscripció. No es faràn inscripcions abans d'aquest moment.")
    inscripcio_fins_a = models.DateTimeField('Inscripció fins a', blank=True,
        null=True, help_text="Fins a quan es permet la "
            "inscripció. No es faràn inscripcions despés d'aquest moment.")
    # Permet preus en [0, 100) (en EUR)
    def _preu_default():
        return Decimal('0.00')
    preu = models.DecimalField(max_digits=4, decimal_places=2, blank=True,
        null=False, default=_preu_default,
        validators=[validators.DecimalValidator(4, 2),
            validators.MinValueValidator(0.00)],
        help_text='Preu en euros. Ha de ser major o igual a 0 i menor que 100')
    cursos = models.ManyToManyField(Curs, blank=True,
        help_text='Els cursos que es poden inscriure')
    alumnes = models.ManyToManyField(Alumne, through='Inscripcio')

    def get_absolute_url(self):
        return reverse('extraescolars:show', args=[self.id_interna])

    def __str__(self):
        return self.nom

class Inscripcio(models.Model):
    class Meta:
        verbose_name = 'inscripció'
        verbose_name_plural = 'inscripcions'
    activitat = models.ForeignKey(Extraescolar, on_delete=models.CASCADE)
    alumne = models.ForeignKey(Alumne, on_delete=models.CASCADE)
    confirmat = models.BooleanField(default=False, help_text="Si s'ha "
        "confirmat (ex. si s'ha enviat la inscripció per correu o si s'ha "
        "lliurat a l'AMPA).")
    pagat = models.BooleanField(default=False, help_text="Si està pagat. "
        "Si el preu de l'activitat és 0 (gratuït), es marcarà automàticament "
        "al guardar.")

    def __str__(self):
        return str(self.alumne) + ' - ' + str(self.activitat)

    # Senyal associada: .signals.inscripcio_pre_save
