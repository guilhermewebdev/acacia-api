# Generated by Django 3.1.3 on 2020-11-20 15:51

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_proposal_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='registration_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='CounterProposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_value', models.FloatField(default=django.db.models.expressions.F('proposal__value'), validators=[django.core.validators.MinValueValidator(65)])),
                ('description', models.TextField()),
                ('registration_date', models.DateTimeField(auto_now=True)),
                ('proposal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='counter_proposal', to='services.proposal')),
            ],
        ),
    ]
