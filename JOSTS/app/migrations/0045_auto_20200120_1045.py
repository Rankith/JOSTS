# Generated by Django 2.2.8 on 2020-01-20 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_videonotetemp'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='bonus',
            field=models.DecimalField(blank=True, decimal_places=1, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='element',
            name='bonus_67',
            field=models.DecimalField(blank=True, decimal_places=1, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='element',
            name='bonus_8',
            field=models.DecimalField(blank=True, decimal_places=1, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='element',
            name='bonus_9',
            field=models.DecimalField(blank=True, decimal_places=1, default=0.0, max_digits=3),
        ),
    ]
