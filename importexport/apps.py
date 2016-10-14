from django.apps import AppConfig


class ImportexportConfig(AppConfig):
    name = 'importexport'

    def ready(self):
        # Registrar senyals
        from . import signals  # pylint: disable=unused-variable
