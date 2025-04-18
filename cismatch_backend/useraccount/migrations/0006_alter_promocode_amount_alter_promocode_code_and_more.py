# Generated by Django 5.1.2 on 2025-01-21 13:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useraccount', '0005_promocode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='code',
            field=models.CharField(max_length=255, unique=True, verbose_name='Промокод'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Создан'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='is_used',
            field=models.BooleanField(default=False, verbose_name='Использован'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователем'),
        ),
        migrations.CreateModel(
            name='PromoCodeHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activated_at', models.DateTimeField(auto_now_add=True)),
                ('promo_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='useraccount.promocode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
