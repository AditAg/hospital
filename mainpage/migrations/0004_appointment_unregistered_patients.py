# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0003_auto_20171003_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unregistered_Patients',
            fields=[
                ('username', models.CharField(primary_key=True, max_length=100, serialize=False)),
                ('email', models.CharField(primary_key=True, max_length=100)),
                ('dob', models.DateField()),
                ('contact', models.IntegerField(max_length=10)),
                ('address', models.CharField(max_length=100)),
                ('street', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=20)),
                ('zip_code', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('patient', models.ForeignKey(primary_key=True, serialize=False, to='mainpage.Unregistered_Patients')),
                ('appointment_date', models.DateField(primary_key=True)),
                ('appointment_time', models.TimeField(primary_key=True)),
                ('department', models.CharField(max_length=100)),
                ('appointment_purpose', models.CharField(max_length=500)),
            ],
        ),
    ]
