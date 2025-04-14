import uuid

from django.conf import settings
from django.db import models

from useraccount.models import User

def images_directory_path(instance, filename):
    return '/'.join(['draws',str(instance.id), str(uuid.uuid4().hex + ".webp")])

class Advert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name='Название блока', blank=True, null=True)
    body = models.TextField(verbose_name='Описание', max_length=2000, blank=True, null=True)
    url = models.CharField(verbose_name='Ссылка переход', max_length=2000, blank=True, null=True)
    image = models.ImageField(upload_to=images_directory_path, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='advert_team')
    published = models.BooleanField(verbose_name='Опубликована', default=True)
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updateAt = models.DateTimeField(auto_now=True)

    def advert_image_url(self):
        if self.image:
            return f'{settings.WEBSITE_URL}{self.image.url}'
    class Meta :
        verbose_name = 'Информационный блок'
        verbose_name_plural = 'Информационные блоки'


class MiniNews(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name='Сама мини новость')
    url = models.CharField(verbose_name='Ссылка переход', max_length=2000, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='mininews_author')
    published = models.BooleanField(verbose_name='Опубликована', default=True)
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updateAt = models.DateTimeField(auto_now=True)

    class Meta :
        verbose_name = 'Мини новости'
        verbose_name_plural = 'Мини новости'