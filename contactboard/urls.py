from django.conf.urls import url, include
from .apps import ContactboardConfig
from . import views

app_name = ContactboardConfig.name
curspatterns = [
    url(r'^add$', views.add_curs, name='add-curs'),
    url(r'^edit/(?P<id_curs>.+)', views.edit_curs, name='edit-curs'),
    url(r'^delete/(?P<id_curs>.+)', views.delete_curs, name='delete-curs')
]
classepatterns = [
    url(r'^add/(?P<id_curs>.+)', views.add_classe, name='add-classe'),
    url(r'^edit/(?P<id_classe>.+)', views.edit_classe, name='edit-classe'),
    url(r'^delete/(?P<id_classe>.+)', views.delete_classe,
        name='delete-classe')
]
urlpatterns = [
    url(r'^list/admin$', views.adminlist, name='adminlist'),
    url(r'^list/(?P<id_classe>.+)', views.list, name='list'),
    url(r'^add/(?P<id_classe>.+)', views.add_alumne, name='add-alumne'),
    url(r'^edit/(?P<alumne_pk>[0-9]+)', views.edit_alumne, name='edit-alumne'),
    url(r'^delete/(?P<alumne_pk>[0-9]+)', views.delete_alumne,
        name='delete-alumne'),
    url(r'^mailto$', views.mailto, name='mailto'),
    url(r'^mailto/(?P<id_classe>.+)', views.mailtoclasse, name='mailto'),
    url(r'^curs/', include(curspatterns)),
    url(r'^classe/', include(classepatterns))
]
