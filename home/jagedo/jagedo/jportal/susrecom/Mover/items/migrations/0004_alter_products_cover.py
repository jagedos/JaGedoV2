# Generated by Django 4.1.1 on 2022-10-04 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0003_alter_products_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='cover',
            field=models.ImageField(default=0, upload_to='products/'),
        ),
    ]
