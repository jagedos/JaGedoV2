# Generated by Django 4.1.1 on 2023-01-04 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='delivery_method',
            field=models.IntegerField(default=0),
        ),
    ]
