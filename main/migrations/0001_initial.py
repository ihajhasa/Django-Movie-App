# Generated by Django 2.0.2 on 2018-07-01 03:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('year', models.IntegerField(default=2018, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2200)])),
                ('rating', models.DecimalField(decimal_places=3, default=0.0, max_digits=4, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('nratings', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]