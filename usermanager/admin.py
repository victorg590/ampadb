from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['alumne']}),
        ('Usuari relacionat', {'fields': ['user', 'unregisteredUser']})
    ]

# class UnregisteredUserAdmin(admin.ModelAdmin):
#     pass
admin.site.register(UnregisteredUser)
