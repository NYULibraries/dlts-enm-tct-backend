# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-06 17:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
    ]
