# Generated by Django 4.2.6 on 2023-10-09 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_posts_likes_alter_posts_parent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='likes',
            field=models.ManyToManyField(blank=True, null=True, to='app.udata'),
        ),
    ]