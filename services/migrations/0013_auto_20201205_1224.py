# Generated by Django 3.1.4 on 2020-12-05 12:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20201203_0029'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0012_auto_20201204_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='client',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='professional',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='core.professional'),
        ),
    ]
