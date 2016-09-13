from django.apps import AppConfig


class ExtraescolarsConfig(AppConfig):
    name = 'extraescolars'
    verbose_name = 'Activitats extraescolars'

    def ready(self):
        from . import signals
