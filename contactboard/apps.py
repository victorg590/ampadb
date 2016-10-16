from django.apps import AppConfig


class ContactboardConfig(AppConfig):
    name = 'contactboard'
    verbose_name = 'Cursos i classes'

    def ready(self):
        # Registrar senyals
        from . import signals  # pylint: disable=unused-variable
