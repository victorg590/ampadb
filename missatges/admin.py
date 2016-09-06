from django.contrib import admin
from .models import GrupDeMissatgeria, Conversacio, Missatge

@admin.register(GrupDeMissatgeria)
class GrupDeMissatgeriaAdmin(admin.ModelAdmin):
    raw_id_fields = ['usuaris']

class MissatgeInline(admin.StackedInline):
    model = Missatge
    extra = 0

@admin.register(Conversacio)
class ConversacioAdmin(admin.ModelAdmin):
    raw_id_fields = ['de']
    list_display = ['assumpte', 'tancat', 'de', 'a']
    list_editable = ['tancat']
    list_filter = ['tancat', 'a']
    search_fields = ['assumpte']
    inlines = [MissatgeInline]
