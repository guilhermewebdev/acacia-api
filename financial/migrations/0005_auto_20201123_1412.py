# Generated by Django 3.1.3 on 2020-11-23 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_auto_20201123_1316'),
        ('financial', '0004_cashout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='job',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='job', to='services.job'),
        ),
    ]
