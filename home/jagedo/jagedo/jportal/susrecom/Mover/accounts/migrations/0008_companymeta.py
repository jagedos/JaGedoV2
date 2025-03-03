# Generated by Django 4.1.1 on 2022-10-25 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_customuser_email_alter_customuser_phone_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('protocol', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'CompanyMeta',
                'verbose_name_plural': 'Company_Meta_Data',
            },
        ),
    ]
