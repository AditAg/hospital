# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorSpeciality',
            fields=[
                ('specialty', models.CharField(primary_key=True, max_length=30, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'Doctors specialties',
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('ssn', models.CharField(max_length=9, unique=True)),
                ('birthday', models.DateField()),
                ('street', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=20)),
                ('zip_code', models.CharField(max_length=5)),
                ('gender', models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])),
            ],
        ),
    ]
