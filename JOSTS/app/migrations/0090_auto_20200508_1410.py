# Generated by Django 2.2.6 on 2020-05-08 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0089_auto_20200508_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementtext',
            name='short_text',
            field=models.CharField(blank=True, default='', max_length=400),
        ),
    ]
