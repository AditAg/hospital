# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-28 06:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0006_auto_20171028_1201'),
        ('doctor', '0012_auto_20171003_0201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='speciality',
        ),
        migrations.RemoveField(
            model_name='doctor',
            name='user',
        ),
        migrations.DeleteModel(
            name='Doctor',
        ),
        migrations.DeleteModel(
            name='DoctorSpeciality',
        ),
    ]
