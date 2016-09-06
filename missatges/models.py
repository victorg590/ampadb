from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class GrupDeMissatgeria(models.Model):
    class Meta:
        verbose_name_plural = 'grups de missatgeria'
    nom = models.CharField(max_length=100)
    usuaris = models.ManyToManyField(User)

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

    def __str__(self):
        if len(self.contingut) > 80:
            return self.contingut[:77] + '...'
        else:
            return self.contingut

class EstatMissatge(models.Model):
    destinatari = models.ForeignKey(User, on_delete=models.CASCADE)
    missatge = models.ForeignKey(Missatge, on_delete=models.CASCADE)
    vist = models.BooleanField(blank=True, default=False)
