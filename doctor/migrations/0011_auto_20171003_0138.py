# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0010_auto_20171003_0130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctorspeciality',
            name='id',
        ),
        migrations.AlterField(
            model_name='doctor',
            name='speciality',
            field=models.ForeignKey(default='Other', to='doctor.DoctorSpeciality'),
        ),
        migrations.AlterField(
            model_name='doctorspeciality',
            name='speciality',
            field=models.CharField(primary_key=True, max_length=30, serialize=False),
        ),
    ]
