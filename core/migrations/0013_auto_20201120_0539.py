# Generated by Django 3.1.3 on 2020-11-20 05:39

import core.models
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20201120_0216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professional',
            name='skills',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('AC', 'Hospital Escort'), ('AD', 'Home Escort'), ('CV', 'Dressings / Vaccines'), ('HC', 'Home Care')], max_length=15, validators=[core.models.ValidateChoices((('AC', 'Hospital Escort'), ('AD', 'Home Escort'), ('CV', 'Dressings / Vaccines'), ('HC', 'Home Care')))]), blank=True, null=True, size=3),
        ),
    ]