# Generated by Django 4.1.1 on 2022-10-05 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_alter_products_cover'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='cover',
        ),
        migrations.AddField(
            model_name='products',
            name='serial',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.CreateModel(
            name='Pimages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Cover', models.ImageField(default='products/none.png', upload_to='products/')),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='items.products')),
            ],
        ),
    ]
