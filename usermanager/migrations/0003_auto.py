# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-11-10 19:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0002_auto'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['alumne'], 'verbose_name': 'perfil'},
        ),
        migrations.AlterModelOptions(
            name='unregistereduser',
            options={'ordering': ['username'], 'verbose_name': 'usuari no registrat', 'verbose_name_plural': 'usuaris no registrats'},
        ),
    ]
