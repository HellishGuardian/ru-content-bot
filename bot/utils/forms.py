from aiogram.fsm.state import StatesGroup, State

class Onboarding(StatesGroup):
    about = State()   # один шаг: свободный текст от пользователя
