from django.utils import timezone
import uuid
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
import requests


class CustomUserManager(UserManager):
    def _create_user(self, name, email, password, **extra_fields):
        if not email:
            email = f"{uuid.uuid4()}@cismatch.ru"
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user
    
    def create_user(self, name=None, email=None , password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(name, email, password, **extra_fields)
    
    def create_superuser(self, name=None, email=None , password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(name, email, password, **extra_fields)
    
def images_directory_path(instance, filename):
    return '/'.join(['avatars',str(instance.id), str(uuid.uuid4().hex + ".webp")])

def backgrounds_directory_path(instance, filename):
    return '/'.join(['backgrounds',str(instance.id), str(uuid.uuid4().hex + ".webp")])

class User(AbstractBaseUser, PermissionsMixin):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True,null=False, blank=False)
    name = models.CharField(max_length=100, blank=True, null=True)

    steam_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    avatar = models.ImageField(upload_to=images_directory_path,blank=True, null=True)
    steam_avatar = models.URLField(blank=True, null=True)
    background_profile = models.ImageField(upload_to=backgrounds_directory_path,blank=True, null=True)
    trade_url = models.URLField(blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    def avatar_url(self):
        if self.avatar:
            return f'{settings.WEBSITE_URL}{self.avatar.url}'
    def background_profile_url(self):
        if self.background_profile:
            return f'{settings.WEBSITE_URL}{self.background_profile.url}'
    class Meta :
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class PromoCode(models.Model):
    code = models.CharField(max_length=255, unique=True, verbose_name='Промокод')
    amount =  models.IntegerField(default=0, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    expires_at = models.DateTimeField(verbose_name='Дата окончания')

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.code
    class Meta :
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        
class PromoCodeHistory(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.name} активировал {self.promo_code.code}'


class SkinBuyOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'), #трейд создан
        ('approved', 'Отправлено'), #трейд отпрален ботом пользователю
        ('accepted', 'Принято'), #трейд принят пользователем
        ('bought', 'Выкуплено'),
        ('paid', 'Оплачено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset_id = models.CharField(max_length=50, verbose_name='ID предмета в Steam') 
    skin_name = models.CharField(max_length=255, verbose_name='Название скина')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    trade_offer_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Трейд оффер')
    image_url = models.CharField(max_length=512, blank=True, null=True, verbose_name='Картинка')  # Ссылка на изображение  # ID трейд-предложения
    payment_id = models.CharField(blank=True, null=True, verbose_name='id оплаты')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    def __str__(self):
        return f"{self.skin_name} ({self.offer_price} ₽) - {self.status}"
    class Meta :
        verbose_name = 'Скупка'
        verbose_name_plural = 'Скупка'