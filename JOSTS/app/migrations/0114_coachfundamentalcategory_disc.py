# Generated by Django 2.2.6 on 2020-06-05 18:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0113_auto_20200603_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='coachfundamentalcategory',
            name='disc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Disc'),
        ),
    ]