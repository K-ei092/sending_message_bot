from aiogram.fsm.state import State, StatesGroup


# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    fill_tz = State()              # Состояние ожидания ввода TZ
    fill_day_scheduler = State()   # Состояние ожидания ввода дней недели для поступления задания, выбранного пользователем
    fill_time_scheduler = State()  # Состояние ожидания ввода времени поступления задания, выбранного пользователем