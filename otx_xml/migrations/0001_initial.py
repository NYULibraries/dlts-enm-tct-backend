# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-26 23:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='XMLPattern',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='default', max_length=255, null=True, unique=True)),
                ('xpath_title', models.CharField(blank=True, max_length=255, null=True)),
                ('xpath_author', models.CharField(blank=True, max_length=255, null=True)),
                ('xpath_location', models.CharField(blank=True, max_length=255, null=True)),
                ('xpath_content', models.CharField(blank=True, max_length=255, null=True)),
                ('xpath_topic', models.CharField(blank=True, max_length=255, null=True)),
                ('xpath_occurrence', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
