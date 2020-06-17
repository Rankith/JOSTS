# Generated by Django 2.2.6 on 2020-06-03 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0112_auto_20200603_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='coachfundamentalsection',
            name='is_graded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coachfundamentalsection',
            name='is_quiz',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coachfundamentalsection',
            name='number_of_questions',
            field=models.IntegerField(default=0),
        ),
    ]