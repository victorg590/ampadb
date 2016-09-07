from django.conf.urls import url
from .apps import MissatgesConfig
from . import views

app_name = MissatgesConfig.name
urlpatterns = [
    url(r'^new$', views.new, name='new'),
    url(r'^compose/(?P<to>[0-9]+)', views.compose, name='compose'),
    url(r'^$', views.list_view, name='list')
]
