from django.contrib import admin
from .models import *

class InscripcioInline(admin.TabularInline):
    model = Inscripcio
    raw_id_fields = ['alumne']
    extra = 1

@admin.register(Extraescolar)
class ExtraescolarAdmin(admin.ModelAdmin):
    inlines = [InscripcioInline]
    prepopulated_fields = {'id_interna': ['nom']}
    list_display = ['nom', 'descripcio_curta']
