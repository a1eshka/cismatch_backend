from celery import shared_task
from django.utils import timezone
from .models import Raffle  # Предполагается, что модель Raffle находится в этом приложении
from celery.schedules import crontab
from cismatch_backend.celery import app  # Импортируем app из cismatch_backend/celery.py

@shared_task
def check_and_draw_raffles():
    now = timezone.now()
    raffles = Raffle.objects.filter(end_time__lte=now, is_drawn=False)

    for raffle in raffles:
        try:
            raffle.draw_winner()  # Используем метод draw_winner() из модели Raffle
        except ValueError as e:
            print(f"Ошибка при розыгрыше {raffle}: {e}")  # Логируем ошибку
