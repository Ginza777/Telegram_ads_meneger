# Generated by Django 4.2.6 on 2023-10-27 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client_settings',
            name='session',
            field=models.FileField(blank=True, null=True, upload_to='Ads_manager/'),
        ),
    ]
