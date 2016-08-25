from django.apps import AppConfig


class UsermanagerConfig(AppConfig):
    name = 'usermanager'

    def ready(self):
        from . import signals  # Registrar senyals
