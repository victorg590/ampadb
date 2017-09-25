from django.conf.urls import url, include
from .apps import ImportexportConfig
from . import views
from . import views_ies

app_name = ImportexportConfig.name
iespatterns = ([
    url(r'upload$', views_ies.upload, name='upload'),
    url(r'classnames/(?P<upload_id>.+)', views_ies.classnames,
        name='classnames'),
    url(r'confirm/(?P<upload_id>.+)', views_ies.confirm, name='confirm'),
    url(r'cancel/(?P<upload_id>.+)', views_ies.cancel, name='cancel')
], 'ies')

urlpatterns = [
    url(r'^export$', views.export_view, name='export'),
    url(r'^export/(?P<classe_id>.+)', views.export_view, name='export'),
    url(r'^genexport$', views.genexport, name='genexport'),
    url(r'^import$', views.import_view, name='import'),
    url(r'^processimport', views.processimport, name='processimport'),
    url(r'^format$', views.format_view, name='format'),
    url(r'^format/template\.csv$', views.download_template,
        name='format-template'),
    url(r'^ies/', include(iespatterns))
]
