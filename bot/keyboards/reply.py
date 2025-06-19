#reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📝 Новая заявка"))
    builder.row(
        KeyboardButton(text="📋 Мои заявки"),
        KeyboardButton(text="🆘 Помощь")
    )
    return builder.as_markup(resize_keyboard=True)

def get_cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить")]],
        resize_keyboard=True
    )

def get_request_type_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔧 Ремонт"),
        KeyboardButton(text="🛒 Покупка"),
        KeyboardButton(text="💸 Расход")
    )
    builder.row(KeyboardButton(text="❌ Отменить"))
    return builder.as_markup(resize_keyboard=True)