# Generated by Django 2.2.8 on 2019-12-30 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_rulelink_videonote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulelink',
            name='category_order',
            field=models.IntegerField(default=0),
        ),
    ]
