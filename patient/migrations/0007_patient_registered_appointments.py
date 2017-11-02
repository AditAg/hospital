# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-28 06:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('patient', '0006_auto_20171028_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('ssn', models.CharField(max_length=9, unique=True)),
                ('birthday', models.DateField()),
                ('street', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=20)),
                ('zip_code', models.CharField(max_length=6)),
                ('gender', models.CharField(choices=[(b'M', b'Male'), (b'F', b'Female')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='registered_appointments',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField()),
                ('department', models.CharField(max_length=100)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='patient.Patient')),
            ],
        ),
    ]