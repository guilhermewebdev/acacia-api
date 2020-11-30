# Generated by Django 3.1.3 on 2020-11-30 14:18

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20201127_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='availability',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
