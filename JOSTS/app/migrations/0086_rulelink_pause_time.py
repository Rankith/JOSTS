# Generated by Django 2.2.11 on 2020-04-27 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0085_video_approved_sts'),
    ]

    operations = [
        migrations.AddField(
            model_name='rulelink',
            name='pause_time',
            field=models.CharField(default='temp', max_length=5),
        ),
    ]
