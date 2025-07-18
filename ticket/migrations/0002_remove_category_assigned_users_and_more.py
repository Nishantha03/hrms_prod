# Generated by Django 5.1.6 on 2025-02-27 10:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='assigned_users',
        ),
        migrations.AddField(
            model_name='category',
            name='assigned_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assign_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
