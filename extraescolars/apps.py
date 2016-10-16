from django.apps import AppConfig


class ExtraescolarsConfig(AppConfig):
    name = 'extraescolars'
    verbose_name = 'Activitats extraescolars'

    def ready(self):
        # Registrar senyals
        from . import signals  # pylint: disable=unused-variable
