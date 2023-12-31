# Generated by Django 4.2.1 on 2023-10-26 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_udata_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="udata",
            name="avatar",
            field=models.ImageField(
                default="avatar.svg", null=True, upload_to="profile_pics"
            ),
        ),
    ]
