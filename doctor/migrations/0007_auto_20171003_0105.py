# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0006_auto_20171003_0039'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='speciality',
            new_name='speciality_doctor',
        ),
    ]
