# Generated by Django 3.1.4 on 2020-12-10 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20201209_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='pagarme_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
