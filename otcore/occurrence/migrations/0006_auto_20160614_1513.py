# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-14 19:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('occurrence', '0005_auto_20160614_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='content_unique_indicator',
            field=models.CharField(max_length=55, unique=True),
        ),
    ]
