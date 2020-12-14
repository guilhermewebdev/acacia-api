# Generated by Django 3.1.4 on 2020-12-12 00:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0013_auto_20201211_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashout',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
