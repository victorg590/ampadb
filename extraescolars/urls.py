from django.conf.urls import url, include
from .apps import ExtraescolarsConfig
from . import views

app_name = ExtraescolarsConfig.name
adminpatterns = [
    url(r'^add$', views.add, name='add'),
    url(r'^edit/(?P<act_id>.+)', views.edit, name='edit'),
    url(r'^delete/(?P<act_id>.+)', views.delete, name='delete'),
    url(r'^inscripcions$', views.inscripcions, name='inscripcions'),
    url(r'^cancel_ins/(?P<ins_pk>.+)', views.cancel_ins, name='cancel-inscripcio')
]
urlpatterns = [
    url(r'^admin/', include(adminpatterns)),
    url(r'^show/(?P<act_id>.+)', views.show, name='show'),
    url(r'^inscripcio/(?P<act_id>.+)', views.inscripcio, name='inscripcio'),
    url(r'^cancel/(?P<act_id>.+)', views.cancel, name='cancel'),
    url(r'^genfull$', views.genfull, name='genfull'),
    url(r'^$', views.list_view, name='list')
]
