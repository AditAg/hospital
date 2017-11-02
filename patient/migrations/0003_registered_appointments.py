# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0002_auto_20171003_1430'),
    ]

    operations = [
        migrations.CreateModel(
            name='registered_appointments',
            fields=[
                ('doctor', models.ForeignKey(primary_key=True, serialize=False, to='doctor.Doctor')),
                ('patient', models.ForeignKey(primary_key=True, to='patient.Patient')),
                ('appointment_date', models.DateField(primary_key=True)),
                ('appointment_time', models.TimeField(primary_key=True)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
    ]
