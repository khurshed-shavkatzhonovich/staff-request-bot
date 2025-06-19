from django.contrib import admin
from .models import StaffRequest
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
import csv

class ExportAsCSV:
    """Класс для экспорта в CSV"""
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.model_name}.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = "Экспорт выбранных в CSV"

@admin.register(StaffRequest)
class StaffRequestAdmin(admin.ModelAdmin, ExportAsCSV):
    list_display = (
        'id', 
        'get_request_type_display', 
        'telegram_user_info',
        'site',
        'description',
        'amount',
        'equipment',
        'created_at',
        'get_status_display',
        'view_link'
    )
    list_filter = (
        'request_type', 
        'status',
        ('created_at', admin.DateFieldListFilter),
    )
    search_fields = (
        'telegram_user_id',
        'telegram_username',
        'full_name',
        'site',
        'equipment',
    )
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    
    # Правильное объявление view_link
    view_link = ['export_as_csv']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('request_type', 'status', 'telegram_user_id', 'telegram_username', 'full_name')
        }),
        ('Детали заявки', {
            'fields': ('site', 'equipment', 'description', 'amount')
        }),
        ('Модерация', {
            'fields': ('approved_by', 'approved_at', 'authorized_by', 'authorized_at'),
            'classes': ('collapse',)
        }),
        ('Технические данные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def telegram_user_info(self, obj):
        return format_html(
            'ID: {}<br>@{}<br>{}',
            obj.telegram_user_id,
            obj.telegram_username or '-',
            obj.full_name or '-'
        )
    telegram_user_info.short_description = 'Пользователь'

    def view_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Просмотр</a>',
            reverse('admin:staffapp_staffrequest_change', args=[obj.id])
        )
    view_link.short_description = ''