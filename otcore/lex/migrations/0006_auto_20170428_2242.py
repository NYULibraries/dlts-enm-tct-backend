# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-29 02:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lex', '0005_auto_20170427_2047'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recognizer',
            options={'ordering': ('priority',)},
        ),
    ]
