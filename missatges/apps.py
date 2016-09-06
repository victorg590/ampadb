from django.apps import AppConfig


class MissatgesConfig(AppConfig):
    name = 'missatges'

    def ready(self):
        from . import signals
