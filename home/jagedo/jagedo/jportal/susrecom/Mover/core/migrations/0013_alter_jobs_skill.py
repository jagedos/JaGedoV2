# Generated by Django 4.1.1 on 2023-02-27 10:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0020_remove_expertskills_description_and_more'),
        ('core', '0012_alter_jobs_skill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='skill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='experts.skills'),
        ),
    ]
