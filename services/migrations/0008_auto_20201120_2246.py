# Generated by Django 3.1.3 on 2020-11-20 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_auto_20201120_2213'),
    ]

    operations = [
        migrations.AddField(
            model_name='counterproposal',
            name='_accepted',
            field=models.BooleanField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='proposal',
            name='_accepted',
            field=models.BooleanField(blank=True, editable=False, null=True),
        ),
    ]
