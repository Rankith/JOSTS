# Generated by Django 2.2.11 on 2020-03-16 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0074_competitiontype_display_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='disc',
        ),
    ]