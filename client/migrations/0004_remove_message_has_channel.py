# Generated by Django 4.2.6 on 2024-01-09 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0003_message_has_channel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='has_channel',
        ),
    ]
