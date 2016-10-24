from django.contrib import admin
from usermanager.admin import ProfileInline
from .models import *


@admin.register(Alumne)
class AlumneAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Informació personal',
            {'fields': [('nom', 'cognoms'), 'classe',
                        ('correu_alumne', 'compartir_correu_alumne'),
                        ('telefon_alumne', 'compartir_telefon_alumne')]}),
        ('Informació de contacte del pare',
            {'fields': [('nom_pare', 'cognoms_pare'),
                        ('correu_pare', 'compartir_correu_pare'),
                        ('telefon_pare', 'compartir_telefon_pare')]}),
        ('Informació de contacte de la mare',
            {'fields': [('nom_mare', 'cognoms_mare'),
                        ('correu_mare', 'compartir_correu_mare'),
                        ('telefon_mare', 'compartir_telefon_mare')]}),
    ]
    inlines = [ProfileInline]
    list_display = ['nom', 'cognoms', 'classe', 'correu_alumne',
                    'telefon_alumne', 'correu_pare', 'telefon_pare',
                    'correu_mare', 'telefon_mare']
    list_editable = ['correu_alumne', 'telefon_alumne', 'correu_pare',
                     'telefon_pare', 'correu_mare', 'telefon_mare']
    search_fields = ['nom', 'cognoms']
    list_filter = ['classe']
    ordering = ['cognoms', 'nom']

class ClasseInline(admin.TabularInline):
    model = Classe
    prepopulated_fields = {'id_interna': ['nom']}
    extra = 0


@admin.register(Curs)
class CursAdmin(admin.ModelAdmin):
    inlines = [ClasseInline]
    prepopulated_fields = {'id_interna': ['nom']}
    list_display = ['nom']
    ordering = ['ordre']
