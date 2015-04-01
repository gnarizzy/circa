# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_20150330_0322'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='buyer',
            field=models.OneToOneField(related_name='buyer_profile', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='seller',
            field=models.OneToOneField(related_name='seller_profile', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
