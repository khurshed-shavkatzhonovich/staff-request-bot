import logging
from aiogram import F, Router, Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from staffapp.models import StaffRequest
from django.utils import timezone


logger = logging.getLogger(__name__)
router = Router()

# Глобальные переменные для конфигурации
bot = None
APPROVER_ID = None
ALLOWED_ID = None

def setup(bot_instance, approver_id, allowed_id):
    """Инициализация конфигурации"""
    global bot, APPROVER_ID, ALLOWED_ID
    bot = bot_instance
    APPROVER_ID = approver_id
    ALLOWED_ID = allowed_id

@sync_to_async
def get_request(request_id):
    """Асинхронное получение заявки"""
    return StaffRequest.objects.get(id=request_id)

@sync_to_async
def save_request(request):
    """Асинхронное сохранение заявки"""
    request.save()

async def update_request_buttons(request, message_text, message_reply_markup):
    """Обновляет кнопки в зависимости от статуса заявки"""
    buttons = []
    
    # Если заявка еще не утверждена - показываем кнопку утверждения
    if request.status != 'approved':
        buttons.append(
            InlineKeyboardButton(
                text="✅ Утвердить",
                callback_data=f"approve:{request.id}"
            )
        )
    
    # Если заявка еще не разрешена - показываем кнопку разрешения
    if request.status != 'allowed':
        buttons.append(
            InlineKeyboardButton(
                text="🔓 Разрешить",
                callback_data=f"allow:{request.id}"
            )
        )
    
    # Если есть активные кнопки - создаем новую клавиатуру
    if buttons:
        new_markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    else:
        new_markup = None
    
    # Обновляем сообщение
    await bot.edit_message_text(
        chat_id=message_reply_markup.chat.id,
        message_id=message_reply_markup.message_id,
        text=message_text,
        reply_markup=new_markup
    )

@router.callback_query(F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery):
    try:
        request_id = int(callback.data.split(":")[1])
        user = callback.from_user
        username = user.username or user.full_name
        
        if user.id not in APPROVER_ID:
            await callback.answer("❌ У вас нет прав на утверждение!", show_alert=True)
            return

        request = await get_request(request_id)
        request.status = 'approved'
        request.approved_by = username
        request.approved_at = timezone.now()
        await save_request(request)
        
        # Формируем текст с обоими действиями
        base_text = callback.message.text.split('\n\n')[0]
        new_text = base_text
        
        # Если было разрешение - добавляем его данные
        if request.authorized_by:
            new_text += f"\n\n🔓 Разрешено: {request.authorized_by}\n⏱ {request.authorized_at.strftime('%d.%m.%Y %H:%M')}"
        
        # Добавляем утверждение
        new_text += f"\n\n✅ Утверждено: {username}\n⏱ {request.approved_at.strftime('%d.%m.%Y %H:%M')}"
        
        # Полностью убираем кнопки после утверждения
        await callback.message.edit_text(
            text=new_text,
            reply_markup=None
        )
        await callback.answer("Заявка утверждена!")
        
    except Exception as e:
        logger.error(f"Ошибка в handle_approve: {e}", exc_info=True)
        await callback.answer("⚠️ Произошла ошибка")

@router.callback_query(F.data.startswith("allow:"))
async def handle_allow(callback: CallbackQuery):
    try:
        request_id = int(callback.data.split(":")[1])
        user = callback.from_user
        username = user.username or user.full_name
        
        if user.id not in ALLOWED_ID:
            await callback.answer("❌ У вас нет прав на разрешение!", show_alert=True)
            return

        request = await get_request(request_id)
        request.status = 'allowed'
        request.authorized_by = username
        request.authorized_at = timezone.now()
        await save_request(request)
        
        # Формируем текст с разрешением
        new_text = f"{callback.message.text.split('\n\n')[0]}\n\n🔓 Разрешено: {username}\n⏱ {request.authorized_at.strftime('%d.%m.%Y %H:%M')}"
        
        # Оставляем только кнопку утверждения
        buttons = [[
            InlineKeyboardButton(
                text="✅ Утвердить",
                callback_data=f"approve:{request.id}"
            )
        ]]
        
        await callback.message.edit_text(
            text=new_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await callback.answer("Заявка разрешена!")
        
    except Exception as e:
        logger.error(f"Ошибка в handle_allow: {e}", exc_info=True)
        await callback.answer("⚠️ Произошла ошибка")

def register_callbacks(dp: Dispatcher):
    """Регистрация обработчиков для совместимости"""
    dp.include_router(router)