# Generated by Django 3.1.3 on 2020-11-20 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_auto_20201120_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='counterproposal',
            name='accepted',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
