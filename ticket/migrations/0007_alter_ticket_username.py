# Generated by Django 5.1.4 on 2025-03-01 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0006_ticket_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='username',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
