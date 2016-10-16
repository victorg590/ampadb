from django.apps import AppConfig


class MissatgesConfig(AppConfig):
    name = 'missatges'

    def ready(self):
        # Registrar senyals
        from . import signals  # pylint: disable=unused-variable
