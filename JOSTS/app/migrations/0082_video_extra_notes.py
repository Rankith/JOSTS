# Generated by Django 2.2.11 on 2020-04-15 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0081_auto_20200410_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='extra_notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
