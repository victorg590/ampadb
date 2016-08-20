from django.conf.urls import url
from .apps import ImportexportConfig
from . import views

app_name = ImportexportConfig.name
urlpatterns = [
    url(r'^export$', views.export_view, name='export'),
    url(r'^export/(?P<classe_id>.+)', views.export_view, name='export'),
    url(r'^genexport$', views.genexport, name='genexport'),
    url(r'^import$', views.import_view, name='import'),
    url(r'^processimport', views.processimport, name='processimport'),
    url(r'^format$', views.format_view, name='format'),
    url(r'^format/template\.csv$', views.download_template, name='format-template')
]
