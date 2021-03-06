# Generated by Django 2.2.6 on 2020-07-24 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0123_acrowomensbonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='acrobalance',
            name='old_id',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='AcroInvalid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invalid_for', models.CharField(blank=True, default='', max_length=3)),
                ('base', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invalid_base', to='app.AcroBalance')),
                ('top', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invalid_top', to='app.AcroBalance')),
            ],
        ),
    ]
