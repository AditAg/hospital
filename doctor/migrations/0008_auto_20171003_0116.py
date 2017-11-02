# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0007_auto_20171003_0105'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='speciality_doctor',
            new_name='speciality',
        ),
    ]
