# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-02 12:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0011_workertype_alive_beat_span'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlackWebhook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('icon_emoji', models.CharField(blank=True, max_length=255, null=True)),
                ('channel', models.CharField(blank=True, max_length=255, null=True)),
                ('apply_global', models.BooleanField(default=True)),
                ('limit_worker_types', models.ManyToManyField(to='core.WorkerType')),
            ],
        ),
    ]