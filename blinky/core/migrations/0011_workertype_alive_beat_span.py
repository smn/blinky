# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-01 15:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20161130_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='workertype',
            name='alive_beat_span',
            field=models.IntegerField(default=3),
        ),
    ]
