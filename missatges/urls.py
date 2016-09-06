from django.conf.urls import url
from .apps import MissatgesConfig
from . import views

app_name = MissatgesConfig.name
urlpatterns = [
    url(r'^$', views.list_view, name='list')
]
