# Generated by Django 2.2.7 on 2019-11-30 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_subscription_interval'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
    ]
