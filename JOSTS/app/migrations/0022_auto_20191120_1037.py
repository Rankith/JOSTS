# Generated by Django 2.2.6 on 2019-11-20 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_symbolduplicates'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SymbolDuplicates',
            new_name='SymbolDuplicate',
        ),
    ]
