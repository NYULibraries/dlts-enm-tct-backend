# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-14 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('occurrence', '0004_auto_20160529_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='content_descriptor',
            field=models.CharField(max_length=255),
        ),
    ]
