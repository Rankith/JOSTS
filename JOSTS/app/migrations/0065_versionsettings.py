# Generated by Django 2.2.8 on 2020-02-28 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0064_videonote_unrated_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='VersionSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
    ]