from django.contrib import admin
from .models import *

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['alumne']}),
        ('Usuari relacionat', {'fields': ['user', 'unregisteredUser']})
    ]
    raw_id_fields = ['alumne', 'user', 'unregisteredUser']

admin.site.register(UnregisteredUser)
