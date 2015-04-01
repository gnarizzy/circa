# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_item_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='auction',
            field=models.OneToOneField(null=True, to='core.Auction'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='buyer',
            field=models.OneToOneField(related_name='buyer_profile', null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='seller',
            field=models.OneToOneField(related_name='seller_profile', null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
