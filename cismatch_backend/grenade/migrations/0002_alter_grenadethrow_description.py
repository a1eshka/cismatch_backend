# Generated by Django 5.1.2 on 2025-04-03 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grenade', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grenadethrow',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
    ]
