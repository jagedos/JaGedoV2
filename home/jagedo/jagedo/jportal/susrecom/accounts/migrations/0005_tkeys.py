# Generated by Django 4.1.1 on 2022-10-17 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tkeys',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('u_name', models.CharField(blank=True, max_length=255)),
                ('u_key', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
