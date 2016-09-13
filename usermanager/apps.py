from django.apps import AppConfig


class UsermanagerConfig(AppConfig):
    name = 'usermanager'
    verbose_name = "Administració d'usuaris"

    def ready(self):
        from . import signals  # Registrar senyals
