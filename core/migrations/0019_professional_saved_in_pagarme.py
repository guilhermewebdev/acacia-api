# Generated by Django 3.1.3 on 2020-11-24 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20201124_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='saved_in_pagarme',
            field=models.BooleanField(default=False),
        ),
    ]