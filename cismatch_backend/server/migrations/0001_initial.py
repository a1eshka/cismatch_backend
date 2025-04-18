# Generated by Django 5.1.2 on 2024-11-15 11:23

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ip', models.CharField(verbose_name='Ip адрес')),
                ('port', models.IntegerField(verbose_name='Порт')),
                ('published', models.BooleanField(default=True, verbose_name='Активна')),
                ('createdAt', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('updateAt', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_server', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Сервер',
                'verbose_name_plural': 'Сервера',
            },
        ),
    ]
