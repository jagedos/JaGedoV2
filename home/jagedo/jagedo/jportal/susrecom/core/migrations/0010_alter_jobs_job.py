# Generated by Django 4.1.1 on 2023-02-25 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0020_remove_expertskills_description_and_more'),
        ('core', '0009_pcarts_expert_alter_pcarts_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='experts.expertcats'),
        ),
    ]
