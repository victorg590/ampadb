from django.apps import AppConfig


class ImportexportConfig(AppConfig):
    name = 'importexport'

    def ready(self):
        from . import signals
