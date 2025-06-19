#models.py
from django.db import models
from django.utils import timezone

class StaffRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('repair', 'Ремонт'),
        ('purchase', 'Покупка'),
        ('expense', 'Расход'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('allowed', 'Разрешено'),
        ('approved', 'Утверждено'),
        ('rejected', 'Отклонено'),
    ]

    # Основная информация о заявке
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE_CHOICES,
        verbose_name="Тип заявки"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )

    # Информация о пользователе
    telegram_user_id = models.BigIntegerField(
        verbose_name="ID пользователя Telegram"
    )
    
    telegram_username = models.CharField(
        max_length=150,
        verbose_name="Имя пользователя Telegram",
        blank=True,
        null=True
    )
    
    full_name = models.CharField(
        max_length=200,
        verbose_name="Полное имя",
        blank=True,
        null=True
    )

    # Информация о сообщении
    telegram_message_id = models.BigIntegerField(
        verbose_name="ID сообщения в Telegram",
        blank=True,
        null=True
    )
    
    telegram_thread_id = models.BigIntegerField(
        verbose_name="ID топика в Telegram",
        blank=True,
        null=True
    )

    # Содержание заявки
    subdivision = models.CharField(
        max_length=100,
        verbose_name="Подразделение",
        default="-"
    )
    
    site = models.CharField(
        max_length=100,
        verbose_name="Участок/Объект"
    )
    
    equipment = models.CharField(
        max_length=150,
        verbose_name="Оборудование",
        blank=True,
        null=True,
        help_text="Заполняется только для заявок на ремонт"
    )
    
    description = models.TextField(
        verbose_name="Описание",
        default="Нет описания",  # Добавляем значение по умолчанию
        help_text="Подробное описание заявки"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма (сомони)",
        blank=True,
        null=True
    )

    # Модерация
    approved_by = models.CharField(
        max_length=100,
        verbose_name="Утвердил",
        blank=True,
        null=True
    )
    
    approved_at = models.DateTimeField(
        verbose_name="Дата утверждения",
        blank=True,
        null=True
    )
    
    authorized_by = models.CharField(
        max_length=100,
        verbose_name="Разрешил",
        blank=True,
        null=True
    )
    
    authorized_at = models.DateTimeField(
        verbose_name="Дата разрешения",
        blank=True,
        null=True
    )

    # Даты
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['request_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_request_type_display()} #{self.id} от {self.telegram_username or self.full_name or self.telegram_user_id}"

    def save(self, *args, **kwargs):
        # Автоматическое обновление дат при изменении статусов
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        if self.status == 'allowed' and not self.authorized_at:
            self.authorized_at = timezone.now()
        super().save(*args, **kwargs)
