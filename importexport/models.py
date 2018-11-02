from datetime import timedelta
from pathlib import PurePath
from django.db import models
from django.db.models import Q, Exists, OuterRef
from django.utils import timezone
from contactboard.models import Classe


class ImportData(models.Model):
    class Meta:
        unique_together = ('importacio', 'nom', 'cognoms')

    importacio = models.ForeignKey('IesImport', on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    cognoms = models.CharField(max_length=255)
    codi_classe = models.CharField(max_length=20)


class IesImport(models.Model):
    eliminar_no_mencionats = models.BooleanField(
        'Eliminar no mencionats',
        default=True,
        help_text="Esborra els alumnes no mencionats de la base de dades")
    ultima_mod = models.DateTimeField('Última modificació', auto_now=True)

    def __str__(self):
        ret = "Importació de {} (Última modificació: {:%d/%m/%Y %H:%M})"\
            .format(
                PurePath(self.ifile.name).name,
                self.ultima_mod
            )
        return ret

    @property
    def act_recent(self):
        """Mostra si hi ha hagut activitat la última setmana"""
        return (timezone.now() - self.ultima_mod) <= timedelta(days=7)

    @classmethod
    def clean_old(cls):
        """Elimina entrades antigues"""
        ultima_setmana = timezone.now() - timedelta(days=7)
        # No modificat en la última setmana O
        # no existeixen ImportData associades
        cond = Q(ultima_mod__lt=ultima_setmana) | ~Exists(
            ImportData.objects.filter(importacio__pk=OuterRef('pk')))
        cls.objects.filter(cond).delete()


class ClassMap(models.Model):
    class Meta:
        unique_together = ('importacio', 'codi_classe')

    importacio = models.ForeignKey(IesImport, on_delete=models.CASCADE)
    codi_classe = models.CharField(max_length=20)
    classe_mapejada = models.ForeignKey(
        Classe, on_delete=models.SET_NULL, null=True, default=None)