# Generated by Django 2.2.6 on 2020-07-24 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0126_acrobalancetransition'),
    ]

    operations = [
        migrations.AddField(
            model_name='acrobalancetransition',
            name='event',
            field=models.CharField(default='XP', max_length=2),
            preserve_default=False,
        ),
    ]