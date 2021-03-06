# Generated by Django 2.2.6 on 2020-06-01 20:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0108_auto_20200529_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoachRules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, default='', max_length=255)),
                ('sub_category', models.CharField(blank=True, default='', max_length=255)),
                ('cue', models.TextField(blank=True, default='')),
                ('response', models.TextField(blank=True, default='')),
                ('disc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Disc')),
            ],
        ),
    ]
