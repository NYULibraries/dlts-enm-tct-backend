# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-07 00:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('occurrence', '0012_auto_20160812_1603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='doctype',
        ),
        migrations.DeleteModel(
            name='DocType',
        ),
    ]
