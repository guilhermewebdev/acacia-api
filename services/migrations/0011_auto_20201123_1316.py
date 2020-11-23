# Generated by Django 3.1.3 on 2020-11-23 13:16

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0015_auto_20201123_1248'),
        ('services', '0010_auto_20201120_2334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='client',
            field=models.ForeignKey(on_delete=models.SET(core.models.User.get_deleted_user), related_name='hires', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='job',
            name='professional',
            field=models.ForeignKey(on_delete=models.SET(core.models.Professional.get_deleted_professional), related_name='jobs', to='core.professional'),
        ),
        migrations.AlterField(
            model_name='job',
            name='proposal',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='job', to='services.proposal'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='client',
            field=models.ForeignKey(on_delete=models.SET(core.models.User.get_deleted_user), related_name='rates', to=settings.AUTH_USER_MODEL),
        ),
    ]
