# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doorguard', '0003_auto_20151006_2039'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='config',
            options={'ordering': ['config_type', 'name', 'value']},
        ),
        migrations.AlterField(
            model_name='config',
            name='config_type',
            field=models.CharField(max_length=10, choices=[('ALARM', 'Alarm-Type'), ('EMAIL', 'Email address'), ('CHECKER', 'Configuration for checker.py')]),
        ),
        migrations.AlterField(
            model_name='config',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='config',
            unique_together=set([('config_type', 'name')]),
        ),
    ]
