# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-30 17:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_users', '0002_auto_20170330_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manageruser',
            options={'verbose_name': 'management user', 'verbose_name_plural': 'management users'},
        ),
        migrations.AlterModelOptions(
            name='organisationuser',
            options={'verbose_name': 'organisation user', 'verbose_name_plural': 'organisation users'},
        ),
        migrations.AlterModelOptions(
            name='province',
            options={'verbose_name': 'province', 'verbose_name_plural': 'provinces'},
        ),
        migrations.AlterModelOptions(
            name='region',
            options={'verbose_name': 'region', 'verbose_name_plural': 'regions'},
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='postal_code',
            field=models.PositiveIntegerField(),
        ),
    ]
