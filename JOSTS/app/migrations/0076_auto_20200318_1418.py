# Generated by Django 2.2.11 on 2020-03-18 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0075_remove_competition_disc'),
    ]

    operations = [
        migrations.AddField(
            model_name='versionsettings',
            name='competition_videos',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='versionsettings',
            name='tcexamples',
            field=models.BooleanField(default=False),
        ),
    ]