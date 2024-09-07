LEXICON: dict[str, str] | dict[str, list[str]] = {
    '/start': 'В заданное время я буду направлять одно задание, которое необходимо выполнить. '
              '\nВечером я напомню об отчете',
    '/help': 'В базе знаний бота более 50 уникальных заданий и рекомендаций. Для того, чтобы не перегружать '
             'тебя информацией, бот отправит всего 30 из них. Если захочешь продолжить, просто отправь боту команду '
             '/start и согласись с предложением.\n\nЕсли нужно прекратить получать сообщения от бота - заблокируй '
             'его в настройках или отправь команду /restart. Это действие сбросит все настройки и пройденные задания',
    '/admin_help': 'Напиши боту сообщение или отправь медиафайл, документ или голосовое сообщение. '
                   'Бот перешлет его всем пользователям.\n\nпересланное сообщение будет содержать ссылку '
                   'на отправителя\n\nДополнительные команды для администратора:\n'
                   '1. Запросить базу данных пользователей в формате Excel -\nкоманда /user_database\n'
                   '2. Удалить из базы данных пользователя - отправьте боту сообщение "УДАЛИТЬ <i>ID_пользователя</i>" '
                   '(например: УДАЛИТЬ 1234567890)\n3. Запросить рейтинг первых 10 мест - команда /statistic',
    'restart': 'Настройки сброшены, можешь запустить бот заново /start',


    'create_keyboar_update_yes': 'Да',
    'create_keyboar_update_no': 'Нет',
    'first_exercise_now': 'Хочу сейчас!',
    'first_exercise_late': 'Позже',
    'create_keyboar_yes': 'ДА',
    'create_keyboar_no': 'НЕТ',
    'create_keyboar_recommendation_implemented': '❤',
    'confirm_restart_keyboard': 'Подтверждаю',
    'confirm_restart_not_keyboard': 'Отмена',


    'admin_message_for_users': 'Отправить всем это сообщение?\n',
    'confirm_restart': 'Подтверди удаление.\nУдалятся все данные и настройки из бота',
    'end_sitings': 'Я записал твои пожелания ✅, а напоминания о благодарности буду присылать в 2️⃣0️⃣:0️⃣0️⃣'
                   '\n\nСоветую ознакомиться с подсказками, нажав на /help',
    'day_scheduler': 'Спасибо! А теперь выбери дни недели, в которые я должен отправлять тебе задания 📅',
    'delete_user': 'Пользователь удалён.',
    'do_not_send': 'Ok! ☑',
    'first_exercise': 'И ещё... могу выслать первое задание сейчас, а могу отложить на потом. Как ты хочешь? 🙂',
    'first_exercise_late_callback': 'Okey! 👌\nВнес в твой график',
    'first_exercise_now_callback': 'Отправляю первое задание.\nИ не забудь поставить лайк ❤ после выполнения, '
                                   'это откроет доступ к заданию следующего дня.',
    'heppy_end': 'ВСЕ ЗАДАНИЯ ВЫПОЛНЕНЫ!',
    'last_task': 'ЭТО ПОСЛЕДНЕЕ ЗАДАНИЕ В БЛОКЕ!\nНАЖМИ /help и узнай, как продолжить',
    'message_forward': 'Ваше сообщение переслано всем пользователям бота',
    'not_restart': 'Команда отменена',
    'not_update_counter': 'Ok! 😎',
    'old_user': 'Хочешь приступить к следующему блоку заданий? 😉',
    'recommendation_implemented': 'Нажми лайк в подтверждение выполнения задания!',
    'reset_counter': 'Отлично! 🥳',
    'state_error': 'Сначала заверши настройки',
    'time_scheduler': 'Отлично! И в завершении выбери время, в которое присылать задания ⏰ \n',
    'time_zone': 'А теперь давай настроим нашу работу, чтобы тебе было комфортнее.\n\n'
                 'Выбери свой часовой пояс 🔎',


    'change_exercise_state': ['✅',
                              'Отдохни до следующего задания',
                              'Следующее задание вскоре будет.',
                              'Ждём следующего задания.',
                              '🔥',
                              'А мы отличные напарники!',
                              'Ты огонь! 🔥',
                              'Блеск! ✨',
                              'Продолжай в том же духе!'
                              ],


    'rating_handlers': ['Блестящие результаты 😎',
                        'Веселая статистика 😄',
                        'Статистическое веселье 🥳',
                        'Битва титанов',
                        'Просто статистика 🥱'
                        ],


    'reminder': ['Подтверди выполнение прошлого задания ❤',
                 'Чтобы получить следующее задание, необходимо нажать на ❤ выше',
                 'Мне нужно знать! Нажми на ❤ выше',
                 'Про ❤ не забудь...',
                 'Разгадай ребус: ☝👉❤✅',
                 'Не настаиваю, но чтобы двигаться дальше, надо нажать ❤ выше',
                 'Про лайк не забываем 🙄'
                 ]
}


LEXICON_COMMANDS: dict[str, str] = {
    '/start': 'Запуск бота / новый блок',
    '/help': 'Помощь',
    '/admin_help': 'Только для админа',
    '/restart': 'Сбросить все настройки'
}


list_flower = [
    '\U0001F338',       # 🌸
    '\U0001F33A',       # 🌺
    '\U0001F339',       # 🌹
    '\U0001F33B',       # 🌻
    '\U0001F4AE',       # 💮
    '\U0001F3F5',       # 🏵
    '\U0001F490',       # 💐
    '\U0001F940',       # 🥀
    '\U0001F33C'        # 🌼
]
