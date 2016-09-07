from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from datetime import timedelta

class GrupDeMissatgeria(models.Model):
    class Meta:
        verbose_name_plural = 'grups de missatgeria'
    nom = models.CharField(max_length=100)
    usuaris = models.ManyToManyField(User)
    motius = models.TextField(blank=True, help_text='Motius per enviar '
        'missatges a aquest grup. Apareixeràn a "Nou missatge". Un per línia.')

    @cached_property
    def motius_list(self):
        # Separar 'motius'. Si hi ha línies en blanc, les elimina.
        return list(filter(None, self.motius.splitlines()))

    def __str__(self):
        return self.nom

class Conversacio(models.Model):
    class Meta:
        verbose_name = 'conversació'
        verbose_name_plural = 'conversacions'

    de = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False,
        null=True)
    a = models.ForeignKey(GrupDeMissatgeria, on_delete=models.SET_NULL,
        blank=False, null=True)
    assumpte = models.CharField(max_length=80)
    tancat = models.BooleanField(blank=True, default=False)

    def __str__(self):
        rstr = self.assumpte
        if self.tancat:
            rstr += ' [TANCAT]'
        return rstr

class EstatMissatge(models.Model):
    destinatari = models.ForeignKey(User, on_delete=models.CASCADE)
    missatge = models.ForeignKey('Missatge', on_delete=models.CASCADE)
    vist = models.BooleanField(blank=True, default=False)

class Missatge(models.Model):
    class Meta:
        unique_together = ('conversacio', 'ordre')
    conversacio = models.ForeignKey(Conversacio, on_delete=models.CASCADE,
        blank=False, null=False, verbose_name='conversació')
    per = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False,
        null=True, related_name='ha_enviat')
    destinataris = models.ManyToManyField(User, through='EstatMissatge')
    ordre = models.PositiveSmallIntegerField(editable=False)
    contingut = models.TextField(blank=False,
        help_text='Suporta <a href="/markdown">Markdown</a>')
    enviat = models.DateTimeField(auto_now_add=True, blank=False,null=False)
    editat = models.DateTimeField(auto_now=True, blank=False, null=False)

    def ha_sigut_editat(self):
        '''Indica si un missatge ha sigut editat'''
        return abs(self.editat - self.enviat) > timedelta(seconds=2)
        # Permet un marge de +/- 2 segons
    ha_sigut_editat.boolean = True
    ha_sigut_editat.short_description = 'Ha sigut editat?'

    def calcular_destinataris(self):
        if not self.per in self.destinataris.all():
            EstatMissatge.objects.create(destinatari=self.per, missatge=self)
        en_grup = self.conversacio.a
        for u in (u for u in self.conversacio.a.usuaris.all()
            if u not in self.destinataris.all()):
            EstatMissatge.objects.create(destinatari=u, missatge=self)
        self.save()

    def __str__(self):
        if len(self.contingut) > 80:
            return self.contingut[:77] + '...'
        else:
            return self.contingut
