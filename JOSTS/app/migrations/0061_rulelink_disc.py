# Generated by Django 2.2.8 on 2020-02-24 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0060_auto_20200224_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='rulelink',
            name='disc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Disc'),
        ),
    ]
