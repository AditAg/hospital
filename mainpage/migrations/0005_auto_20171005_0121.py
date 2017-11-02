# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0004_appointment_unregistered_patients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unregistered_patients',
            name='email',
            field=models.CharField(primary_key=True, max_length=100, serialize=False),
        ),
        migrations.AlterField(
            model_name='unregistered_patients',
            name='username',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
