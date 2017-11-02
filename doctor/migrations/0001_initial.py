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
            name='Doctor',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_doctor', models.BooleanField(default=True)),
                ('specialization', models.CharField(max_length=100)),
                ('certification', models.CharField(max_length=30, choices=[('A', 'American Board'), ('B', 'Bachelor')])),
            ],
        ),
    ]
