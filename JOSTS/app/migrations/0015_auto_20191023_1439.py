# Generated by Django 2.2.6 on 2019-10-23 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_rule_rules'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Rules',
            new_name='RuleText',
        ),
        migrations.RenameField(
            model_name='ruletext',
            old_name='rule_descriptions',
            new_name='rule_description',
        ),
        migrations.AddField(
            model_name='rule',
            name='event',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
    ]
