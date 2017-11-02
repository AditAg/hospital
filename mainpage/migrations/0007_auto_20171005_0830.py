# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0006_auto_20171005_0125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.OneToOneField(primary_key=True, serialize=False, to='mainpage.Unregistered_Patients'),
        ),
        migrations.AlterField(
            model_name='unregistered_patients',
            name='contact',
            field=models.CharField(max_length=10),
        ),
    ]
