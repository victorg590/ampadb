from django.conf.urls import url, include
from .apps import UsermanagerConfig
from . import views

adminpatterns = [
    url(r'^new$', views.new_admin, name='new-admin'),
    url(r'^new/(?P<alumne_pk>[0-9]{1,30})', views.new_user, name='new-user'),
    url(r'^delete/(?P<username>[\w.@+-]{1,30})', views.delete_user, name='delete'),
    url(r'^cancel/(?P<username>[\w.@+-]{1,30})', views.cancel_user, name='cancel'),
    url(r'^changepassword/(?P<username>[\w.@+-]{1,30})', views.admin_changepassword,
        name='admin-changepassword'),
    url(r'^changecode/(?P<username>[\w.@+-]{1,30})/auto',
        views.change_code_auto, name='change-code-auto'),
    url(r'^changecode/(?P<username>[\w.@+-]{1,30})', views.change_code,
        name='change-code'),
    url(r'^$', views.list_users, name='list')
]
accountpatterns = [
    url(r'^register$', views.register, name='register'),
    url(r'^', include('django.contrib.auth.urls'))
]
urlpatterns = [
    url(r'^accounts/', include(accountpatterns)),
    url(r'^users/', include(adminpatterns, namespace=UsermanagerConfig.name))
]
