# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0011_auto_20171003_0138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorspeciality',
            name='label',
            field=models.CharField(primary_key=True, max_length=10, serialize=False),
        ),
        migrations.AlterField(
            model_name='doctorspeciality',
            name='speciality',
            field=models.CharField(max_length=30),
        ),
    ]
