# Generated by Django 2.2.7 on 2019-11-30 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_subscriptiontest'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptiontest',
            name='type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
