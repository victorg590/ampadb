from django.apps import AppConfig


class ContactboardConfig(AppConfig):
    name = 'contactboard'
    verbose_name = 'Cursos i classes'

    def ready(self):
        from . import signals  # Registrar senyals
