# Generated by Django 2.2.11 on 2020-03-16 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0073_versionsettings_use_level_slider'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitiontype',
            name='display_order',
            field=models.IntegerField(default=1),
        ),
    ]