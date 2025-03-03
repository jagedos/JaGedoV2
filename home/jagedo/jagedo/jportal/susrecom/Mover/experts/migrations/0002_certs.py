# Generated by Django 4.1.1 on 2022-12-27 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Certs',
                'verbose_name_plural': 'Required_Certificate_List',
            },
        ),
    ]
