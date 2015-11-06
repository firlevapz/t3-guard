# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doorguard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('config_type', models.CharField(max_length=10, choices=[('ALARM', 'Alarm enabled'), ('EMAIL', 'Email address')])),
                ('value', models.CharField(unique=True, max_length=30)),
                ('enabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='device',
            name='ip',
            field=models.GenericIPAddressField(unique=True, protocol='ipv4'),
        ),
    ]
