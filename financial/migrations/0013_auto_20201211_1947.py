# Generated by Django 3.1.4 on 2020-12-11 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0012_auto_20201211_1923'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cashout',
            old_name='pagerme_id',
            new_name='pagarme_id',
        ),
    ]
