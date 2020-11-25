# Generated by Django 3.1.3 on 2020-11-24 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0008_payment_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashout',
            name='pagerme_id',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='cashout',
            name='withdrawn',
            field=models.BooleanField(default=False),
        ),
    ]
