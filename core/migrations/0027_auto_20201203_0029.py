# Generated by Django 3.1.4 on 2020-12-03 00:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_professional_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='celphone',
            new_name='cellphone',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='celphone_ddd',
            new_name='cellphone_ddd',
        ),
    ]
