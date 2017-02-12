from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^markdown$', views.markdown_help, name='markdown-help'),
    url(r'^searchsyntax$', views.search_syntax, name='search-syntax'),
    url(r'^$', views.index, name='index')
]
