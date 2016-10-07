from django.db import models
from django.utils import timezone
from datetime import timedelta
from io import StringIO
from pathlib import PurePath

class IesImport(models.Model):
    ifile = models.FileField("Arxiu d'importació", upload_to='uploads/import',
        blank=False, null=False)
    class_dict = models.TextField('Mapa de classes', default='{}',
        help_text="Un text en format JSON que descriu com associar les classes "
        "de l'arxiu a les classes de la base de dades. Una entrada amb 'null' "
        "eliminarà la classe: "'{"<pk classe>": [<nom a l\'arxiu>, ...] | '
        'null, ...}\' Ex. \'{"1": ["1 ESO A"], "2": null}')
    delete_other = models.BooleanField('Eliminar no mencionats', default=True,
        help_text="Esborra els alumnes no mencionats de la base de dades")
    last_mod = models.DateTimeField('Última modificació', auto_now=True)

    def __str__(self):
        ret = "Importació de {} (Última modificació: {:%d/%m/%Y %H:%M})".format(
            PurePath(self.ifile.name).name,
            self.last_mod
        )
        return ret

    @property
    def recent_act(self):
        """Mostra si hi ha hagut activitat la última setmana"""
        return (timezone.now() - self.last_mod) <= timedelta(days=7)

    @classmethod
    def clean_old(cls):
        """Elimina entrades antigues"""
        instances = cls.objects.all()
        for i in instances:
            if not i.recent_act:
                i.delete()
                continue
            f = StringIO()
            try:
                f = i.ifile.open()
            except FileNotFoundError:
                i.delete()
                continue
            finally:
                if f is None:
                    f = StringIO()
                f.close()

    # Senyal associada: .signals.iesimport_pre_delete
