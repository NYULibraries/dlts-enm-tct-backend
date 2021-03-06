# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-29 14:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('occurrence', '0003_auto_20160504_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='occurrence.Document'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='input_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inputs', to='occurrence.Location'),
        ),
    ]
