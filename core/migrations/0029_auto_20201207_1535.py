# Generated by Django 3.1.4 on 2020-12-07 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_user_pagarme_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='pagarme_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]