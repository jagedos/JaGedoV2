# Generated by Django 4.1.1 on 2022-10-10 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vproducts',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
