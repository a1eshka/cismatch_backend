from django.db import models
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta

class GrenadeThrow(models.Model):
    TYPE_CHOICES = [
        ('smoke', 'Smoke'),
        ('flash', 'Flash'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название раскидки')  # Название раскидки
    grenade_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Тип гранаты')  # Смоук или флешка
    map_name = models.CharField(max_length=50, verbose_name='Название карты')  # Название карты
    description = models.TextField(null=True, blank=True,verbose_name='Описание') 
    video_webm_url = models.URLField(verbose_name='Ссылка на WebM-видео')  # Ссылка на WebM-видео
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.map_name}) - {self.grenade_type}"
    
    class Meta :
        verbose_name = 'Граната'
        verbose_name_plural = 'Гранаты'
