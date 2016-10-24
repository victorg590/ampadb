from django.contrib import admin
from .models import *


class ProfileInline(admin.StackedInline):
    model = Profile
    raw_id_fields = ['user', 'unregisteredUser']

admin.site.register(UnregisteredUser)
