# Generated by Django 5.1.7 on 2025-03-29 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees_attendance', '0004_attendance_approved_at_attendance_approved_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='user_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
