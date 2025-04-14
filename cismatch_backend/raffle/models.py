from django.db import models
from django.utils import timezone
import random
from django.db.models import Q
from useraccount.models import User

class Skin(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    price_in_tickets = models.IntegerField(verbose_name='Стоимость, если 0 то бесплатный')  # Стоимость одного тикета для покупки
    image_url = models.CharField(max_length=510, verbose_name='Ссылка на картинку')  # URL изображения скина
    is_active = models.BooleanField(default=True, verbose_name='Активен')  # Скин доступен для покупки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')  # Время создания скина

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Скин'
        verbose_name_plural = 'Скины'


class Raffle(models.Model):
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE, related_name='raffles', verbose_name='Скин')  # Связь с Skin
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='Время начала')  # Время начала розыгрыша
    end_time = models.DateTimeField(verbose_name='Время конца')  # Время окончания розыгрыша
    is_drawn = models.BooleanField(default=False, verbose_name='Разыгран')  # Были ли проведены результаты
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_raffles', verbose_name='Победитель')  # Победитель
    total_tickets = models.PositiveIntegerField(default=100, verbose_name='Билетов всего')  # Общее количество билетов
    remaining_tickets = models.PositiveIntegerField(default=100, verbose_name='Билетов доступно')  # Оставшиеся билеты

    class Meta:
        verbose_name = 'Розыгрыш'
        verbose_name_plural = 'Розыгрыши'

    def __str__(self):
        return f"Raffle for {self.skin.name}"

    def save(self, *args, **kwargs):
        """
        Убедимся, что количество оставшихся билетов не превышает общее количество билетов.
        """
        if self.remaining_tickets is None:
            self.remaining_tickets = self.total_tickets
        self.remaining_tickets = max(0, min(self.remaining_tickets, self.total_tickets))
        super().save(*args, **kwargs)


    def draw_winner(self):
        """
        Проводит розыгрыш среди купленных тикетов.
        """
        if self.is_drawn:
            raise ValueError("Raffle has already been drawn.")
        if timezone.now() < self.end_time:
            raise ValueError("Raffle is not over yet.")

        tickets = Ticket.objects.filter(raffle=self)
        total_tickets = tickets.count()  # Получаем количество купленных билетов

        if total_tickets == 0:
            raise ValueError("No tickets available to draw a winner.")

    # Выбираем случайный индекс
        random_index = random.randint(0, total_tickets - 1)
    
    # Получаем билет по индексу
        winner_ticket = tickets[random_index]

    # Сохраняем победителя
        self.winner = winner_ticket.user
        self.is_drawn = True
        self.save()


    def is_active_raffle(self):
        """
        Проверка, активен ли розыгрыш (не завершён и время не вышло).
        """
        return timezone.now() < self.end_time and not self.is_drawn


class Ticket(models.Model):
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE)  # Связь с розыгрышем
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Пользователь, купивший билет
    created_at = models.DateTimeField(auto_now_add=True)  # Время покупки билета

    def __str__(self):
        return f"Ticket for {self.raffle.skin.name} by {self.user.username}"

    class Meta:
        verbose_name = 'Тикет'
        verbose_name_plural = 'Тикеты'
        
class Task(models.Model):
    TYPE_CHOICES = [
        ("daily", "Ежедневное"),
        ("username", "Изменение имени"),
        ("subscribe", "Подписка"),
        ("custom", "Другое условие"),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    reward = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Награда")
    task_type = models.CharField(max_length=20, default='daily', choices=TYPE_CHOICES, verbose_name="Тип задания")
    condition = models.TextField(blank=True, null=True, verbose_name="Условие (ссылка)")  # Например, ссылка на подписку
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='Время окончания')  # Время окончания розыгрыша
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
    
class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} - {self.task.title} ({'Выполнено' if self.completed else 'Не выполнено'})"
    class Meta:
        verbose_name = 'Выполненное задание'
        verbose_name_plural = 'Выполненные задания'
       
