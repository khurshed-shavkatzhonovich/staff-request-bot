# bot/handlers/form_handlers.py
from django.utils import timezone
from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from staffapp.models import StaffRequest
from decimal import Decimal
import logging
from bot.handlers.states import Form
from asgiref.sync import sync_to_async


logger = logging.getLogger(__name__)


# Глобальные переменные для зависимостей
bot_instance = None
dp_instance = None
TARGET_CHAT_ID = None

def setup(bot, dp, target_chat_id):
    """Инициализация зависимостей"""
    global bot_instance, dp_instance, TARGET_CHAT_ID
    bot_instance = bot
    dp_instance = dp
    TARGET_CHAT_ID = target_chat_id

# Клавиатуры
def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 Новая заявка")]],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить")]],
        resize_keyboard=True
    )

def get_request_type_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔧 Ремонт"), KeyboardButton(text="🛒 Покупка")],
            [KeyboardButton(text="💸 Расход"), KeyboardButton(text="❌ Отменить")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите тип заявки"
    )

# Обработчики
async def start_handler(message: Message):
    """Обработка команды /start"""
    try:
        await message.answer(
            "Добро пожаловать в бот для заявок!",
            reply_markup=get_main_kb()
        )
        logger.info(f"User {message.from_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in start_handler: {e}")

async def new_request_handler(message: Message, state: FSMContext):
    """Начало создания заявки"""
    try:
        await state.clear()
        await message.answer(
            "Выберите тип заявки:",
            reply_markup=get_request_type_kb()
        )
        await state.set_state(Form.request_type)
        logger.info(f"User {message.from_user.id} started new request")
    except Exception as e:
        logger.error(f"Error in new_request_handler: {e}")
        await message.answer("Ошибка при создании заявки", reply_markup=get_main_kb())

async def process_request_type(message: Message, state: FSMContext):
    """Обработка выбора типа заявки"""
    try:
        if message.text == "❌ Отменить":
            await message.answer("Действие отменено", reply_markup=get_main_kb())
            await state.clear()
            return
        
        type_mapping = {
            "🔧 Ремонт": "repair",
            "🛒 Покупка": "purchase",
            "💸 Расход": "expense"
        }
        
        if message.text not in type_mapping:
            await message.answer("Пожалуйста, выберите тип из предложенных вариантов")
            return
        
        await state.update_data(request_type=type_mapping[message.text])
        await state.set_state(Form.site)
        await message.answer("Введите участок (объект):", reply_markup=get_cancel_kb())
        logger.info(f"User {message.from_user.id} selected request type: {message.text}")
    except Exception as e:
        logger.error(f"Error in process_request_type: {e}")
        await message.answer("Ошибка при выборе типа заявки", reply_markup=get_main_kb())
        await state.clear()

async def process_site(message: Message, state: FSMContext):
    """Обработка ввода участка"""
    try:
        if message.text == "❌ Отменить":
            await message.answer("Действие отменено", reply_markup=get_main_kb())
            await state.clear()
            return
            
        await state.update_data(site=message.text)
        data = await state.get_data()
        
        if data["request_type"] == "repair":
            await state.set_state(Form.equipment)
            await message.answer("Введите оборудование для ремонта:", reply_markup=get_cancel_kb())
        else:
            await state.set_state(Form.description)
            await message.answer("Введите описание:", reply_markup=get_cancel_kb())
        
        logger.info(f"User {message.from_user.id} entered site: {message.text}")
    except Exception as e:
        logger.error(f"Error in process_site: {e}")
        await message.answer("Ошибка при вводе участка", reply_markup=get_main_kb())
        await state.clear()

async def process_equipment(message: Message, state: FSMContext):
    """Обработка ввода оборудования"""
    try:
        if message.text == "❌ Отменить":
            await message.answer("Действие отменено", reply_markup=get_main_kb())
            await state.clear()
            return
            
        await state.update_data(equipment=message.text)
        await state.set_state(Form.description)
        await message.answer("Введите описание проблемы:", reply_markup=get_cancel_kb())
        logger.info(f"User {message.from_user.id} entered equipment: {message.text}")
    except Exception as e:
        logger.error(f"Error in process_equipment: {e}")
        await message.answer("Ошибка при вводе оборудования", reply_markup=get_main_kb())
        await state.clear()

async def process_description(message: Message, state: FSMContext):
    """Обработка ввода описания"""
    try:
        if message.text == "❌ Отменить":
            await message.answer("Действие отменено", reply_markup=get_main_kb())
            await state.clear()
            return
            
        await state.update_data(description=message.text)
        await state.set_state(Form.currency)
        await message.answer("Введите валюту:", reply_markup=get_currency_kb())
        logger.info(f"User {message.from_user.id} entered description: {message.text}")
    except Exception as e:
        logger.error(f"Error in process_description: {e}")
        await message.answer("Ошибка при вводе описания", reply_markup=get_main_kb())
        await state.clear()

async def process_currency(message: Message, state: FSMContext):
    """Обработка выбора валюты"""
    try:
        if message.text == "❌ Отменить":
            await message.answer("Действие отменено", reply_markup=get_main_kb())
            await state.clear()
            return

        currency_map = {
            "🇹🇯 Сомони": "TJS",
            "🇷🇺 Рубль": "RUB",
            "🇺🇸 Доллар": "USD"
        }

        if message.text not in currency_map:
            await message.answer("Пожалуйста, выберите валюту из предложенных")
            return

        await state.update_data(currency=currency_map[message.text])
        await state.set_state(Form.amount)
        await message.answer("Введите сумму:", reply_markup=get_cancel_kb())

    except Exception as e:
        logger.error(f"Error in process_currency: {e}")
        await message.answer("Ошибка при выборе валюты", reply_markup=get_main_kb())
        await state.clear()

# Асинхронная обертка для создания заявки
@sync_to_async
def create_staff_request(user_id, username, full_name, request_type, site, equipment, description, amount, currency):
    """Асинхронное создание заявки"""
    try:
        return StaffRequest.objects.create(
            telegram_user_id=user_id,
            telegram_username=username,
            full_name=full_name,
            request_type=request_type,
            site=site,
            equipment=equipment,  # Может быть None
            currency=currency,
            description=description,
            amount=amount,
            status="pending",
            subdivision="-",  # Добавляем обязательное поле
            created_at=timezone.now()  # Явно указываем дату создания
        )
    except Exception as e:
        logger.error(f"Error in create_staff_request: {e}")
        raise

@sync_to_async
def save_request_with_message_id(request, message_id):
    """Асинхронное сохранение с message_id"""
    if not request or not hasattr(request, 'save'):
        raise ValueError("Некорректный объект заявки")
    request.telegram_message_id = message_id
    request.save(update_fields=['telegram_message_id'])

@sync_to_async
def save_request_with_message_id(request, message_id):
    """Асинхронное сохранение с message_id"""
    request.telegram_message_id = message_id
    request.save()

def get_currency_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇹🇯 Сомони"), KeyboardButton(text="🇷🇺 Рубль"), KeyboardButton(text="🇺🇸 Доллар")],
            [KeyboardButton(text="❌ Отменить")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите валюту"
    )


async def process_amount(message: Message, state: FSMContext):
    """Обработка ввода суммы и создание заявки"""
    try:
        if message.text == "❌ Отменить":
            await message.answer("Действие отменено", reply_markup=get_main_kb())
            await state.clear()
            return
            
        try:
            amount = Decimal(str(message.text.replace(",", ".")))
        except Exception:
            await message.answer("Пожалуйста, введите корректную сумму")
            return
        
        data = await state.get_data()
        
        # Создаем заявку
        request = await create_staff_request(
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            request_type=data["request_type"],
            site=data["site"],
            equipment=data.get("equipment", None),  # Явно указываем None вместо пустой строки
            description=data["description"],
            currency=data.get("currency", "TJS"),
            amount=amount
        )
        
        # Убедимся, что заявка создана и имеет ID
        if not request or not request.id:
            raise ValueError("Заявка не была создана или не имеет ID")
        
        # Формируем сообщение
        data = await state.get_data()
        currency = data.get("currency", "TJS")  # по умолчанию сомони
        msg = (
            f"<b>Новая заявка #{request.id}</b>\n"
            f"Тип: {request.get_request_type_display()}\n"
            f"Участок: {request.site}\n"
        )
        if request.equipment:
            msg += f"Оборудование: {request.equipment}\n"
        msg += (
            f"Описание: {request.description}\n"
            f"Сумма: {request.amount} {currency}\n"
            f"От: @{message.from_user.username or message.from_user.full_name}"
        )
        
        # Создаем кнопки с явным преобразованием ID в строку
        buttons = [
            [InlineKeyboardButton(
                text="✅ Утвердить", 
                callback_data=f"approve:{request.pk}"  # Используем pk вместо id
            )],
            [InlineKeyboardButton(
                text="🔓 Разрешить", 
                callback_data=f"allow:{request.pk}"
            )]
        ]
        
        # Отправляем в группу
        sent_message = await bot_instance.send_message(
            chat_id=TARGET_CHAT_ID,
            text=msg,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

        # Сохраняем ID сообщения
        await save_request_with_message_id(request, sent_message.message_id)

        await message.answer("✅ Заявка успешно создана!", reply_markup=get_main_kb())
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка создания заявки: {str(e)}", exc_info=True)
        await message.answer("Ошибка при создании заявки", reply_markup=get_main_kb())
        await state.clear()

def register_handlers(dp):
    """Регистрация всех обработчиков"""
    dp.message.register(start_handler, CommandStart())
    dp.message.register(new_request_handler, F.text == "📝 Новая заявка")
    dp.message.register(process_request_type, Form.request_type)
    dp.message.register(process_site, Form.site)
    dp.message.register(process_equipment, Form.equipment)
    dp.message.register(process_description, Form.description)
    dp.message.register(process_currency, Form.currency)
    dp.message.register(process_amount, Form.amount)
