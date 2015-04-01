# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_auto_20150401_0412'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='buy_now_price',
            field=models.DecimalField(default=1.1, max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='auction',
            name='current_bidder',
            field=models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='auction',
            name='duration',
            field=models.IntegerField(default=3, choices=[(1, '1 day'), (3, '3 days'), (5, '5 days')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='auction',
            name='end_date',
            field=models.DateTimeField(default=datetime.date.today),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='auction',
            name='start_date',
            field=models.DateTimeField(default=datetime.date(2015, 4, 1), auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='auction',
            name='starting_bid',
            field=models.DecimalField(default=1.0, max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='photo1',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='photo2',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='photo3',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
    ]
