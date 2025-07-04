# Generated by Django 5.2.1 on 2025-06-15 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffrequest',
            name='purchase_description',
        ),
        migrations.AddField(
            model_name='staffrequest',
            name='description',
            field=models.TextField(default='Нет описания', help_text='Подробное описание заявки', verbose_name='Описание'),
        ),
        migrations.AddField(
            model_name='staffrequest',
            name='full_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Полное имя'),
        ),
        migrations.AddField(
            model_name='staffrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидает'), ('allowed', 'Разрешено'), ('approved', 'Утверждено'), ('rejected', 'Отклонено')], default='pending', max_length=10, verbose_name='Статус'),
        ),
        migrations.AddField(
            model_name='staffrequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Сумма (сомони)'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='equipment',
            field=models.CharField(blank=True, help_text='Заполняется только для заявок на ремонт', max_length=150, null=True, verbose_name='Оборудование'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='site',
            field=models.CharField(max_length=100, verbose_name='Участок/Объект'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='subdivision',
            field=models.CharField(default='-', max_length=100, verbose_name='Подразделение'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='telegram_message_id',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='ID сообщения в Telegram'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='telegram_thread_id',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='ID топика в Telegram'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='telegram_user_id',
            field=models.BigIntegerField(verbose_name='ID пользователя Telegram'),
        ),
        migrations.AlterField(
            model_name='staffrequest',
            name='telegram_username',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Имя пользователя Telegram'),
        ),
        migrations.AddIndex(
            model_name='staffrequest',
            index=models.Index(fields=['status'], name='staffapp_st_status_1e6646_idx'),
        ),
        migrations.AddIndex(
            model_name='staffrequest',
            index=models.Index(fields=['request_type'], name='staffapp_st_request_8f8551_idx'),
        ),
        migrations.AddIndex(
            model_name='staffrequest',
            index=models.Index(fields=['created_at'], name='staffapp_st_created_0c6e25_idx'),
        ),
    ]
