from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


# Функция для генерации инлайн-клавиатуры в ответ на команду start
def create_update():
    button_yes = InlineKeyboardButton(text=LEXICON['create_keyboar_update_yes'], callback_data='^yes^')
    button_no = InlineKeyboardButton(text=LEXICON['create_keyboar_update_no'], callback_data='^no^')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_yes], [button_no]])
    return keyboard


# Функция для генерации инлайн-клавиатуры для выбора когда отправить задание (сейчас/потом)
def create_keyboard_first_exercise():
    button_yes = InlineKeyboardButton(text=LEXICON['first_exercise_now'], callback_data='^now^')
    button_no = InlineKeyboardButton(text=LEXICON['first_exercise_late'], callback_data='^late^')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_yes], [button_no]])
    return keyboard


# Функция для генерации инлайн-клавиатуры для принятия решения о пересылке сообщения админа пользователям
def create_keyboar(message_id_for_users):
    button_yes = InlineKeyboardButton(text=LEXICON['create_keyboar_yes'], callback_data=f'YES^{message_id_for_users}')
    button_no = InlineKeyboardButton(text=LEXICON['create_keyboar_no'], callback_data='NO^')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_yes], [button_no]])
    return keyboard


# Функция для генерации инлайн-клавиатуры для подтверждения выполнения рекомендации пользователем - ставит ❤
def create_keyboar_recommendation_implemented():
    button_yes = InlineKeyboardButton(
        text=LEXICON['create_keyboar_recommendation_implemented'],
        callback_data='recommendation_implemented'
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_yes]])
    return keyboard


# Функция для генерации инлайн-клавиатуры с часовыми поясами
def create_keyboard_time_zone():
    kb_builder = InlineKeyboardBuilder()
    button_tz_Europe = InlineKeyboardButton(text='МСК -2', callback_data='Europe/Berlin')
    button_tz_Kaliningrad = InlineKeyboardButton(text='МСК -1', callback_data='Europe/Kaliningrad')
    button_tz_0 = InlineKeyboardButton(text='МСК', callback_data='Europe/Moscow')
    button_tz_1 = InlineKeyboardButton(text='МСК +1', callback_data='Europe/Samara')
    button_tz_2 = InlineKeyboardButton(text='МСК +2', callback_data='Asia/Yekaterinburg')
    button_tz_3 = InlineKeyboardButton(text='МСК +3', callback_data='Asia/Omsk')
    button_tz_4 = InlineKeyboardButton(text='МСК +4', callback_data='Asia/Novosibirsk')
    button_tz_5 = InlineKeyboardButton(text='МСК +5', callback_data='Asia/Irkutsk')
    button_tz_6 = InlineKeyboardButton(text='МСК +6', callback_data='Asia/Yakutsk')
    button_tz_7 = InlineKeyboardButton(text='МСК +7', callback_data='Asia/Vladivostok')
    button_tz_8 = InlineKeyboardButton(text='МСК +8', callback_data='Asia/Magadan')
    button_tz_9 = InlineKeyboardButton(text='МСК +9', callback_data='Asia/Kamchatka')
    buttons: list[InlineKeyboardButton] = [
        button_tz_Europe, button_tz_Kaliningrad, button_tz_0, button_tz_1,
        button_tz_2, button_tz_3, button_tz_4, button_tz_5, button_tz_6,
        button_tz_7, button_tz_8, button_tz_9
        ]
    kb_builder.row(*buttons, width=4)
    return kb_builder.as_markup()


# Функция для генерации инлайн-клавиатуры выбора дней отправки заданий
def create_keyboard_day_scheduler():
    button_weekdays = InlineKeyboardButton(text='будни', callback_data='mon-fri')
    button_every_day = InlineKeyboardButton(text='каждый день', callback_data='mon-sun')
    button_odd = InlineKeyboardButton(text='нечетные дни', callback_data='mon,wed,fri,sun')
    button_even = InlineKeyboardButton(text='чётные дни', callback_data='tue,thu,sat')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_weekdays],
        [button_every_day],
        [button_odd],
        [button_even],
    ])
    return keyboard


# Функция для генерации инлайн-клавиатуры выбора времени отправки заданий
def create_keyboard_time_scheduler():
    kb_builder = InlineKeyboardBuilder()
    button_06 = InlineKeyboardButton(text='06:00', callback_data='6')
    button_07 = InlineKeyboardButton(text='07:00', callback_data='7')
    button_08 = InlineKeyboardButton(text='08:00', callback_data='8')
    button_09 = InlineKeyboardButton(text='09:00', callback_data='9')
    button_10 = InlineKeyboardButton(text='10:00', callback_data='10')
    button_11 = InlineKeyboardButton(text='11:00', callback_data='11')
    button_12 = InlineKeyboardButton(text='12:00', callback_data='12')
    button_13 = InlineKeyboardButton(text='13:00', callback_data='13')
    button_14 = InlineKeyboardButton(text='14:00', callback_data='14')
    buttons: list[InlineKeyboardButton] = [
        button_06, button_07, button_08,
        button_09, button_10, button_11,
        button_12, button_13, button_14
    ]
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup()


# Функция для генерации инлайн-клавиатуры подтверждения обнуления бота
def create_keyboard_confirm_restart():
    kb_builder = InlineKeyboardBuilder()
    button_confirm = InlineKeyboardButton(text=LEXICON['confirm_restart_keyboard'], callback_data='^confirm_restart^')
    button_confirm_not = InlineKeyboardButton(text=LEXICON['confirm_restart_not_keyboard'],
                                              callback_data='^confirm_restart_not^')
    buttons: list[InlineKeyboardButton] = [button_confirm, button_confirm_not]
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()
