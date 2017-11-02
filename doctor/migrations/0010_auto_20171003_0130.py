# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0009_auto_20171003_0119'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='speciality_d',
            new_name='speciality',
        ),
        migrations.AddField(
            model_name='doctorspeciality',
            name='id',
            field=models.AutoField(verbose_name='ID', primary_key=True, default=4, serialize=False, auto_created=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='doctorspeciality',
            name='speciality',
            field=models.CharField(max_length=30),
        ),
    ]
