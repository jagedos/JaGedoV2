# Generated by Django 4.1.1 on 2022-10-20 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_tkeys'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tkeys',
            options={'verbose_name': 'Tkeys', 'verbose_name_plural': 'SMS_Keys'},
        ),
        migrations.AddField(
            model_name='profile',
            name='v_key',
            field=models.CharField(blank=True, default=0, max_length=255),
        ),
        migrations.AddField(
            model_name='profile',
            name='v_type',
            field=models.CharField(blank=True, default=0, max_length=255),
        ),
    ]
