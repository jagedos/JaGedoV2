# Generated by Django 4.1.1 on 2023-02-13 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0009_alter_vproducts_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='shops',
            name='is_fundi',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vproducts',
            name='is_fundi',
            field=models.BooleanField(default=False),
        ),
    ]
