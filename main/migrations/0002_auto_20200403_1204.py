# Generated by Django 2.0.2 on 2020-04-03 09:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='year',
            field=models.IntegerField(default=2020, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2200)]),
        ),
    ]
