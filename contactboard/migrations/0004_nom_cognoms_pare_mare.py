# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-28 18:31
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('contactboard', '0003_split_compartir'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumne',
            name='cognoms_mare',
            field=models.CharField(blank=True, max_length=255, verbose_name='cognoms de la mare'),
        ),
        migrations.AddField(
            model_name='alumne',
            name='cognoms_pare',
            field=models.CharField(blank=True, max_length=255, verbose_name='cognoms del pare'),
        ),
        migrations.AddField(
            model_name='alumne',
            name='nom_mare',
            field=models.CharField(blank=True, max_length=255, verbose_name='nom de la mare'),
        ),
        migrations.AddField(
            model_name='alumne',
            name='nom_pare',
            field=models.CharField(blank=True, max_length=255, verbose_name='nom del pare'),
        ),
        migrations.AlterField(
            model_name='alumne',
            name='telefon_alumne',
            field=models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(regex=re.compile('\n    ^\n    ((\\+|00)34)?  # Accepta prefixos (+34/0034)\n    [679][0-9]{8}\n    $\n    ', 96))], verbose_name="telèfon de l'alumne"),
        ),
        migrations.AlterField(
            model_name='alumne',
            name='telefon_mare',
            field=models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(regex=re.compile('\n    ^\n    ((\\+|00)34)?  # Accepta prefixos (+34/0034)\n    [679][0-9]{8}\n    $\n    ', 96))], verbose_name='telèfon de la mare'),
        ),
        migrations.AlterField(
            model_name='alumne',
            name='telefon_pare',
            field=models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(regex=re.compile('\n    ^\n    ((\\+|00)34)?  # Accepta prefixos (+34/0034)\n    [679][0-9]{8}\n    $\n    ', 96))], verbose_name='telèfon del pare'),
        ),
    ]