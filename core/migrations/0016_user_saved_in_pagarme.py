# Generated by Django 3.1.3 on 2020-11-23 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20201123_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saved_in_pagarme',
            field=models.BooleanField(default=False),
        ),
    ]
