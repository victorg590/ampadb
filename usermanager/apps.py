from django.apps import AppConfig


class UsermanagerConfig(AppConfig):
    name = 'usermanager'
    verbose_name = "Administració d'usuaris"

    def ready(self):
        # Registrar senyals
        from . import signals  # pylint: disable=unused-variable
