# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorSpeciality',
            fields=[
                ('speciality', models.CharField(primary_key=True, max_length=30, serialize=False)),
                ('label', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'Doctors specialties',
            },
        ),
        migrations.AddField(
            model_name='doctor',
            name='speciality',
            field=models.ForeignKey(default=None, to='doctor.DoctorSpeciality'),
        ),
    ]
