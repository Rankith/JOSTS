# Generated by Django 2.2.8 on 2019-12-16 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_unsubscribefeedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unsubscribefeedback',
            name='other_details',
            field=models.TextField(blank=True, default=''),
        ),
    ]
