from django.contrib import admin
from .models import GrupDeMissatgeria, Conversacio, Missatge, EstatMissatge


@admin.register(GrupDeMissatgeria)
class GrupDeMissatgeriaAdmin(admin.ModelAdmin):
    raw_id_fields = ['usuaris']


class MissatgeInline(admin.StackedInline):
    model = Missatge
    extra = 0


@admin.register(Conversacio)
class ConversacioAdmin(admin.ModelAdmin):
    raw_id_fields = ['de']
    list_display = ['assumpte', 'tancada', 'creada', 'de', 'a']
    list_editable = ['tancada']
    list_filter = ['tancada', 'a']
    search_fields = ['assumpte']
    inlines = [MissatgeInline]


@admin.register(EstatMissatge)
class EstatMissatgeAdmin(admin.ModelAdmin):
    raw_id_fields = ['destinatari', 'missatge']
    list_display = ['pk', 'missatge', 'destinatari', 'vist']
    list_editable = ['vist']
    list_filter = ['vist']
