from datetime import timedelta
import uuid
from django.db import models, transaction
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from contactboard.models import Classe


class ImportData(models.Model):
    class Meta:
        unique_together = ('importacio', 'nom', 'cognoms')

    importacio = models.ForeignKey(
        'IesImport',
        on_delete=models.CASCADE,
        related_name='dades_relacionades')
    nom = models.CharField(max_length=255)
    cognoms = models.CharField(max_length=255)
    codi_classe = models.CharField(max_length=20)

    def __str__(self):
        return '[{}] {} {} => {}'.format(self.importacio, self.nom,
                                         self.cognoms, self.codi_classe)


class IesImport(models.Model):
    id_importacio = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nom_importacio = models.CharField(max_length=50)
    eliminar_classes_buides = models.BooleanField(
        default=True, help_text="Esborra les classes que quedin buides")
    ultima_mod = models.DateTimeField('Última modificació', auto_now=True)
    canvis_calculats = models.BooleanField(default=False)

    def __str__(self):
        ret = "Importació de {} (Última modificació: {:%d/%m/%Y %H:%M})"\
            .format(
                self.nom_importacio,
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
        te_referencies = Exists(
            ImportData.objects.filter(importacio__pk=OuterRef('pk')))
        condicio_antiga = (Q(ultima_mod__lt=ultima_setmana)
                           | Q(te_referencies=False))
        with transaction.atomic():
            cls.objects.annotate(te_referencies=te_referencies).filter(
                condicio_antiga).delete()


class ClassMap(models.Model):
    class Meta:
        unique_together = ('importacio', 'codi_classe')

    importacio = models.ForeignKey(IesImport, on_delete=models.CASCADE)
    codi_classe = models.CharField(max_length=20)
    classe_mapejada = models.ForeignKey(
        Classe, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return '[{}] {} => {}'.format(self.importacio, self.codi_classe,
                                      self.classe_mapejada)
