from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Alumne)
class AlumneAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Informació personal',
            {'fields': ['nom', 'cognoms', 'classe', 'data_de_naixement',
            'correu_alumne']}),
        ('Informació de contacte del pare',
            {'fields': ['correu_pare', 'telefon_pare'],
            'classes': ['collapse']}),
        ('Informació de contacte de la mare',
            {'fields': ['correu_mare', 'telefon_mare'],
            'classes': ['collapse']}),
        (None, {'fields': ['compartir']})
    ]
    list_display = ['cognoms', 'nom', 'classe']
    search_fields = ['nom', 'cognoms']
    ordering = ['cognoms', 'nom']

class ClasseInline(admin.TabularInline):
    model = Classe
    extra = 0

@admin.register(Curs)
class CursAdmin(admin.ModelAdmin):
    inlines = [ClasseInline]
    ordering = ['ordre']
