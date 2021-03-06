# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-09 20:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manuscripts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='indexpattern',
            old_name='indicator_of_see',
            new_name='see_split_string',
        ),
        migrations.RemoveField(
            model_name='indexpattern',
            name='indicator_of_seealso',
        ),
        migrations.RemoveField(
            model_name='indexpattern',
            name='xpath_occurrence_link_attribute',
        ),
        migrations.RemoveField(
            model_name='indexpattern',
            name='xpath_occurrence_link_element',
        ),
        migrations.AddField(
            model_name='indexpattern',
            name='see_also_split_string',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
