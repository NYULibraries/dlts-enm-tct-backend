# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 23:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('occurrence', '0007_auto_20160615_1859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='occurrence',
            old_name='input_location',
            new_name='location',
        ),
    ]
