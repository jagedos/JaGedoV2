# Generated by Django 4.1.1 on 2022-12-13 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_profile_is_approved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_expert',
            field=models.BooleanField(default=False),
        ),
    ]
