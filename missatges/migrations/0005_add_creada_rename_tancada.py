# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-09 19:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('missatges', '0004_change_verbose_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conversacio',
            options={'ordering': ['creada', 'tancada'], 'verbose_name': 'conversació', 'verbose_name_plural': 'conversacions'},
        ),
        migrations.RenameField(
            model_name='conversacio',
            old_name='tancat',
            new_name='tancada',
        ),
        migrations.AddField(
            model_name='conversacio',
            name='creada',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]