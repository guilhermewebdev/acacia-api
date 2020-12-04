# Generated by Django 3.1.3 on 2020-11-26 15:40

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20201125_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professional',
            name='avg_price',
            field=models.FloatField(blank=True, default=0, null=True, validators=[core.models.MinOrNullValidator(65)], verbose_name='Average Price'),
        ),
    ]