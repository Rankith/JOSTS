# Generated by Django 2.2.11 on 2020-03-23 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0077_auto_20200318_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='TCExample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(max_length=1)),
                ('year', models.CharField(max_length=4)),
                ('short_name', models.CharField(max_length=3)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Video')),
            ],
        ),
    ]