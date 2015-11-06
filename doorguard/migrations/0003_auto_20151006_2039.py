# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doorguard', '0002_auto_20151006_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='name',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='config_type',
            field=models.CharField(max_length=10, choices=[('ALARM', 'Alarm enabled'), ('EMAIL', 'Email address'), ('CHECKER', 'Configuration for checker.py')]),
        ),
        migrations.AlterField(
            model_name='config',
            name='value',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='config',
            unique_together=set([('config_type', 'value')]),
        ),
    ]
