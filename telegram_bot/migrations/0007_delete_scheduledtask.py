# Generated by Django 4.1.3 on 2023-01-23 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0006_merge_20230114_0804'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ScheduledTask',
        ),
    ]
