# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-24 03:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hit', '0010_auto_20160620_0925'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basket',
            options={'ordering': ['preferred_name']},
        ),
        migrations.AddField(
            model_name='hit',
            name='kind',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
