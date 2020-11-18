# Generated by Django 3.1.3 on 2020-11-18 21:57

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default=0, height_field=300, upload_to='avatars', verbose_name='Avatar', width_field=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='born',
            field=models.DateField(default=0, verbose_name='Birth date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='celphone',
            field=models.CharField(default=0, max_length=11),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='telephone',
            field=models.CharField(default=django.utils.timezone.now, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='professional',
            name='avg_price',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(65)], verbose_name='Average Price'),
        ),
    ]
