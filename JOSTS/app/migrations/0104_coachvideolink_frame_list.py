# Generated by Django 2.2.6 on 2020-05-27 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0103_auto_20200525_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='coachvideolink',
            name='frame_list',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]