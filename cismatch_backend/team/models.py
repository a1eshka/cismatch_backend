import uuid

from django.conf import settings
from django.db import models

from useraccount.models import User

def images_directory_path(instance, filename):
    return '/'.join(['teams',str(instance.id), str(uuid.uuid4().hex + ".webp")])

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name='Название команды')
    body = models.TextField(verbose_name='Описание', max_length=2000, blank=True, null=True)
    logo = models.ImageField(upload_to=images_directory_path, blank=True, null=True)
    social_url = models.TextField(verbose_name='Сайт команды', blank=True, null=True, max_length=2000)
    teammates = models.ManyToManyField(User, verbose_name='Участники команды', related_name='teammates')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='author_team')
    published = models.BooleanField(verbose_name='Активна', default=True)
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updateAt = models.DateTimeField(auto_now=True)

    def logo_url(self):
        if self.logo:
            return f'{settings.WEBSITE_URL}{self.logo.url}'
    class Meta :
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
