# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0003_registered_appointments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registered_appointments',
            name='doctor',
            field=models.OneToOneField(primary_key=True, serialize=False, to='doctor.Doctor'),
        ),
        migrations.AlterField(
            model_name='registered_appointments',
            name='patient',
            field=models.OneToOneField(primary_key=True, to='patient.Patient'),
        ),
    ]
