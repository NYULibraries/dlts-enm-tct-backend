# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-29 18:29
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations
import otcore.hit.models
import otcore.lex.lex_utils


class Migration(migrations.Migration):

    dependencies = [
        ('hit', '0002_auto_20160429_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hit',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, max_length=512, populate_from=otcore.hit.models.pop_from, slugify=otcore.lex.lex_utils.lex_slugify),
        ),
    ]
