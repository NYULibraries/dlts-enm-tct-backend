# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 19:45
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manuscripts', '0012_remove_indexpattern_is_subentry_a_separate_element'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indexpattern',
            name='see_split_string',
        ),
        migrations.AddField(
            model_name='indexpattern',
            name='see_split_strings',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), default=[], size=None),
            preserve_default=False,
        ),
    ]
