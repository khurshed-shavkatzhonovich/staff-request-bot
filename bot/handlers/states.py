# bot/states.py
from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    request_type = State()  # Новое начальное состояние
    site = State()
    equipment = State()
    description = State()
    amount = State()