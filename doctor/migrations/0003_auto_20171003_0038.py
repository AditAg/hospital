# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0002_auto_20171002_2203'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='doctor',
            table='doctor_Doctor',
        ),
    ]
