# Generated by Django 2.2.6 on 2020-07-08 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0121_remove_acrobalance_disc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acrobalance',
            name='category',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]