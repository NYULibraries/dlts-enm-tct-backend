# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-19 18:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hit', '0004_auto_20160504_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hit',
            name='angle',
        ),
        migrations.DeleteModel(
            name='Angle',
        ),
    ]
