# Generated by Django 2.2.7 on 2019-11-30 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_subscription_canceled'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscription',
            old_name='canceled',
            new_name='cancelled',
        ),
    ]
