from django.conf.urls import url
from .apps import ExtraescolarsConfig
from . import views

app_name = ExtraescolarsConfig.name
urlpatterns = [
    url(r'^show/(?P<act_id>.+)', views.show, name='show'),
    url(r'^inscripcio/(?P<act_id>.+)', views.inscripcio, name='inscripcio'),
    url(r'^cancel/(?P<act_id>.+)', views.cancel, name='cancel'),
    url(r'^genfull$', views.genfull, name='genfull'),
    url(r'^$', views.list_view, name='list')
]
