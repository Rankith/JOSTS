# Generated by Django 2.2.6 on 2019-11-20 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20191115_1219'),
    ]

    operations = [
        migrations.CreateModel(
            name='SymbolDuplicates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(blank=True, default='', max_length=255)),
                ('replace_with', models.CharField(blank=True, default='', max_length=255)),
                ('event', models.CharField(blank=True, default='', max_length=2)),
            ],
        ),
    ]
