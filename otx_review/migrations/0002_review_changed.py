# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-14 05:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otx_review', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='changed',
            field=models.BooleanField(default=False),
        ),
    ]
