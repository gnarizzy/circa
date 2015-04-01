# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150401_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 1, 20, 39, 48, 189811)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='auction',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 1, 20, 39, 48, 188811), auto_now_add=True),
            preserve_default=True,
        ),
    ]
