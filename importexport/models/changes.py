from django.db import models
from contactboard.models import Classe, Alumne
from .models import IesImport, ImportData


class CanviImportacio(models.Model):
    class Meta:
        abstract = True

    importacio = models.ForeignKey(
        IesImport, on_delete=models.CASCADE, related_name='canvis_%(class)s')
    dada_relacionada = models.OneToOneField(
        ImportData, on_delete=models.CASCADE, related_name='canvi_%(class)s')


class AddAlumne(CanviImportacio):
    nova_classe = models.ForeignKey(
        Classe, on_delete=models.PROTECT, related_name='alumnes_nous')

    def __str__(self):
        return '{} => {}'.format(self.dada_relacionada, self.nova_classe)


class MoveAlumne(CanviImportacio):
    antiga_classe = models.ForeignKey(  # TODO: Redundant (= alumne.classe)
        Classe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alumnes_moguts_de')
    nova_classe = models.ForeignKey(
        Classe, on_delete=models.PROTECT, related_name='alumnes_moguts_a')
    alumne = models.ForeignKey(
        Alumne, on_delete=models.CASCADE, related_name='canvis_classe')

    def __str__(self):
        return '{} => {} -> {}'.format(self.alumne, self.antiga_classe,
                                       self.nova_classe)


class DeleteAlumne(CanviImportacio):
    dada_relacionada = None
    alumne = models.ForeignKey(
        Alumne, on_delete=models.CASCADE, related_name='eliminacions')
    antiga_classe = models.ForeignKey(  # TODO: Redundant (= alumne.classe)
        Classe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alumnes_antics')

    def __str__(self):
        return '{} ~ {}'.format(self.alumne, self.antiga_classe)


class DeleteClasse(CanviImportacio):
    dada_relacionada = None
    classe = models.ForeignKey(
        Classe, on_delete=models.CASCADE, related_name='eliminacions')

    def __str__(self):
        return str(self.classe)
