# Generated by Django 4.1.3 on 2023-01-11 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0004_user_has_used_promocode'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='has_used_promocode',
            new_name='has_activated_promocode',
        ),
    ]
