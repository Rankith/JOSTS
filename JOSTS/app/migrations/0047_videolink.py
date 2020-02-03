# Generated by Django 2.2.8 on 2020-01-31 21:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20200120_1136'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=1)),
                ('frame_jump', models.IntegerField(default=0)),
                ('element', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Element')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Video')),
            ],
        ),
    ]