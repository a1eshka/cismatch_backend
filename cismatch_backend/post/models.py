import uuid

from django.conf import settings
from django.db import models

from useraccount.models import User

def images_directory_path(instance, filename):
    return '/'.join(['posts',str(instance.id), str(uuid.uuid4().hex + ".webp")])

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    body = models.TextField(verbose_name='Описание', max_length=2000)
    type = models.ForeignKey('TypePost', on_delete=models.CASCADE, verbose_name='Тип поста', null=True, blank=True, related_name='type_post')
    status = models.ForeignKey('Status', on_delete=models.CASCADE, verbose_name='Статус', null=True, blank=True, related_name='status_post')
    role = models.ForeignKey('Role', on_delete=models.CASCADE,verbose_name='Роль в игре', null=True, blank=True, related_name='role_post')
    images = models.ImageField(upload_to=images_directory_path, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='user_post')
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    published = models.BooleanField(verbose_name='Опубликован', default=True)
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Опубликовано')
    updateAt = models.DateTimeField(auto_now=True)

    def image_url(self):
        if self.images:
            return f'{settings.WEBSITE_URL}{self.images.url}'
        
    def increment_views(self):
        """Метод увеличивает счетчик просмотров"""
        self.views += 1
        self.save(update_fields=['views'])
        
    class Meta :
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
    
    class Meta :
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class TypePost(models.Model):
    title = models.TextField(max_length=50, db_index=True , verbose_name='Тип поста', blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL сделки')
       
    def __str__(self):
        return self.title
    class Meta :
        verbose_name = 'Тип поста'
        verbose_name_plural = 'Типы поста'


class Status(models.Model):
    title = models.TextField(max_length=50, db_index=True , verbose_name='Статус поста', blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL сделки')
       
    def __str__(self):
        return self.title
    class Meta :
        verbose_name = 'Статус поста'
        verbose_name_plural = 'Статусы поста'


class Role(models.Model):
    title = models.TextField(max_length=50, db_index=True , verbose_name='Роль в игре', blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL')
       
    def __str__(self):
        return self.title
    class Meta :
        verbose_name = 'Роль в игре'
        verbose_name_plural = 'Роли в игре'



