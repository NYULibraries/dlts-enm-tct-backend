# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-15 18:42
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion
import otcore.hit.models
import otcore.lex.lex_utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('topic', '0002_delete_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(db_index=True, max_length=512, unique=True)),
                ('tokengroups', models.ManyToManyField(blank=True, to='topic.Tokengroup')),
                ('types', models.ManyToManyField(blank=True, related_name='baskets', to='topic.Ttype')),
            ],
            options={
                'ordering': ['topic_name__name'],
            },
        ),
        migrations.CreateModel(
            name='Hit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=512)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=512, populate_from=otcore.hit.models.pop_from, slugify=otcore.lex.lex_utils.lex_slugify)),
                ('hidden', models.BooleanField(default=False)),
                ('preferred', models.BooleanField(default=False)),
                ('bypass', models.BooleanField(default=False)),
                ('basket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='topic_name', to='hit.Basket')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(db_index=True, default='Generic', max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='hit',
            name='scope',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, to='hit.Scope'),
        ),
        migrations.AlterUniqueTogether(
            name='hit',
            unique_together=set([('name', 'scope')]),
        ),
    ]
