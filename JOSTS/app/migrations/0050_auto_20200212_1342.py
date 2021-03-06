# Generated by Django 2.2.8 on 2020-02-12 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0049_auto_20200203_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitylog',
            name='disc',
            field=models.CharField(default='WAG', max_length=5),
        ),
        migrations.AddField(
            model_name='drawnimage',
            name='disc',
            field=models.CharField(default='WAG', max_length=5),
        ),
        migrations.AddField(
            model_name='element',
            name='disc',
            field=models.CharField(default='WAG', max_length=5),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='disc',
            field=models.CharField(default='WAG', max_length=5),
        ),
        migrations.AddField(
            model_name='rule',
            name='disc',
            field=models.CharField(default='WAG', max_length=5),
        ),
        migrations.AddField(
            model_name='symbolduplicate',
            name='disc',
            field=models.CharField(default='WAG', max_length=5),
        ),
        migrations.AddField(
            model_name='video',
            name='disc',
            field=models.CharField(default='WAG', max_length=5),
        ),
    ]
