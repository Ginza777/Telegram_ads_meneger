# Generated by Django 4.2.6 on 2024-02-20 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0007_remove_message_has_channel'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Message_history',
        ),
    ]
