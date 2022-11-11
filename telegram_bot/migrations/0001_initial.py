# Generated by Django 4.1.3 on 2022-11-11 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(db_index=True, unique=True)),
                ('is_trial_period', models.BooleanField(default=True)),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
