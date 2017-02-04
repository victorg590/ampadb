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
        ('Informació de contacte del tutor 1',
            {'fields': [('nom_tutor_1', 'cognoms_tutor_1'),
                        ('correu_tutor_1', 'compartir_correu_tutor_1'),
                        ('telefon_tutor_1', 'compartir_telefon_tutor_1')]}),
        ('Informació de contacte del tutor 2',
            {'fields': [('nom_tutor_2', 'cognoms_tutor_2'),
                        ('correu_tutor_2', 'compartir_correu_tutor_2'),
                        ('telefon_tutor_2', 'compartir_telefon_tutor_2')]}),
    ]
    inlines = [ProfileInline]
    list_display = ['nom', 'cognoms', 'classe', 'correu_alumne',
                    'telefon_alumne', 'correu_tutor_1', 'telefon_tutor_1',
                    'correu_tutor_2', 'telefon_tutor_2']
    list_editable = ['correu_alumne', 'telefon_alumne', 'correu_tutor_1',
                     'telefon_tutor_1', 'correu_tutor_2', 'telefon_tutor_2']
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
