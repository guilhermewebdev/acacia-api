# Generated by Django 3.1.4 on 2020-12-11 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0011_auto_20201207_2204'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cashout',
            old_name='withdrawn',
            new_name='was_withdrawn',
        ),
    ]