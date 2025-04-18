# Generated by Django 5.1.2 on 2024-12-24 14:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffle', '0002_alter_raffle_options_alter_skin_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skin',
            name='total_tickets',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='skin',
        ),
        migrations.AddField(
            model_name='raffle',
            name='remaining_tickets',
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AddField(
            model_name='raffle',
            name='total_tickets',
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AddField(
            model_name='ticket',
            name='raffle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='raffle.raffle'),
        ),
        migrations.AlterField(
            model_name='raffle',
            name='skin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raffles', to='raffle.skin'),
        ),
        migrations.AlterField(
            model_name='raffle',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='won_raffles', to=settings.AUTH_USER_MODEL),
        ),
    ]
