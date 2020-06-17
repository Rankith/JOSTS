# Generated by Django 2.2.6 on 2020-06-17 17:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0116_coachfundamentalslide_interaction_random_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoachFundamentalUserQuiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_order', models.IntegerField(default=0)),
                ('slide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.CoachFundamentalSlide')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]