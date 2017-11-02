# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0004_auto_20171005_0828'),
    ]

    operations = [
        migrations.AddField(
            model_name='registered_appointments',
            name='id',
            field=models.AutoField(verbose_name='ID', primary_key=True, default=10, serialize=False, auto_created=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registered_appointments',
            name='appointment_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='registered_appointments',
            name='appointment_time',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='registered_appointments',
            name='doctor',
            field=models.OneToOneField(to='doctor.Doctor'),
        ),
        migrations.AlterField(
            model_name='registered_appointments',
            name='patient',
            field=models.OneToOneField(to='patient.Patient'),
        ),
    ]
