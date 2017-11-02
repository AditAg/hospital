# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0007_auto_20171005_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unregistered_patients',
            name='username',
            field=models.CharField(max_length=100),
        ),
    ]
