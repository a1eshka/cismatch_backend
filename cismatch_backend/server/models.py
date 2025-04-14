from time import timezone
import uuid

from django.conf import settings
from django.db import models
from useraccount.models import User

def images_directory_path(instance, filename):
    return '/'.join(['servers/maps/',str(instance.id), str(uuid.uuid4().hex + ".webp")])

class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip = models.CharField(verbose_name='Ip адрес')
    port = models.IntegerField(verbose_name='Порт')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='author_server')
    published = models.BooleanField(verbose_name='Активна', default=True)
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updateAt = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return f"{self.ip}:{self.port}"
    
    class Meta :
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'

class ServerType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, verbose_name='Название типа')
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updateAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тип сервера'
        verbose_name_plural = 'Типы серверов'

class ThirdPartyServer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip = models.CharField(max_length=100, verbose_name='IP адрес')
    port = models.IntegerField(verbose_name='Порт')
    server_type = models.ForeignKey('ServerType', on_delete=models.SET_NULL, null=True, verbose_name='Тип сервера')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец', related_name='owned_third_party_servers')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    published = models.BooleanField(verbose_name='Активна', default=True)
    is_paid = models.BooleanField(default=False, verbose_name='Платный сервер')
    is_boosted = models.BooleanField(default=False, verbose_name='Поднят в списке')
    boost_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания поднятия')
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updateAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Сторонний сервер: {self.ip}:{self.port}"

    def is_boost_active(self):
        """Проверяет, активно ли поднятие сервера."""
        return self.is_boosted and self.boost_expires_at and self.boost_expires_at > timezone.now()

    class Meta:
        verbose_name = 'Сторонний сервер'
        verbose_name_plural = 'Сторонние серверы'