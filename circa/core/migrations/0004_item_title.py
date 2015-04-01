# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150330_0334'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='title',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
