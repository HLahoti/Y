# Generated by Django 4.2.6 on 2023-10-09 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_posts_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='parent',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.posts'),
        ),
    ]
