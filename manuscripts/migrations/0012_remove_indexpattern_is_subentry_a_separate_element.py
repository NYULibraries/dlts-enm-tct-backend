# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-17 18:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manuscripts', '0011_auto_20161116_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indexpattern',
            name='is_subentry_a_separate_element',
        ),
    ]
