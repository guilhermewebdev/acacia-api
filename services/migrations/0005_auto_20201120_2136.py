# Generated by Django 3.1.3 on 2020-11-20 21:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_auto_20201120_1551'),
    ]

    operations = [
        migrations.RenameField(
            model_name='counterproposal',
            old_name='target_value',
            new_name='value',
        ),
        migrations.RenameField(
            model_name='proposal',
            old_name='end',
            new_name='end_datetime',
        ),
        migrations.RenameField(
            model_name='proposal',
            old_name='start',
            new_name='start_datetime',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='accepted',
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(default=django.db.models.expressions.F(django.db.models.expressions.F('proposal__counter_proposal__value')), validators=[django.core.validators.MinValueValidator(65)])),
                ('registration_date', models.DateTimeField(auto_now=True)),
                ('start_datetime', models.DateTimeField(default=django.db.models.expressions.F('proposal__start_datetime'))),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('proposal', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='job', to='services.proposal')),
            ],
        ),
    ]