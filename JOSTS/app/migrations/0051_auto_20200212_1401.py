# Generated by Django 2.2.8 on 2020-02-12 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0050_auto_20200212_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=10)),
                ('folder_name', models.CharField(max_length=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='element',
            name='disc',
        ),
    ]
