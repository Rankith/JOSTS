# Generated by Django 2.2.8 on 2020-03-02 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0065_versionsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='versionsettings',
            name='rule_sub_header',
            field=models.CharField(default='Section', max_length=30),
        ),
    ]
