from aiogram import types
from dispatcher import dp
from bot import BotDB
from db import DATABASE

WELCOME_TEXT = """
Приветствую! Я бот для чатов, ругаюсь в ответ на аудиосообщения.
Собственно, пока это всё.
Если у вас не в почете людишки, записывающие аудио,
смело добавляйте меня в чат.
Просто отправь мне голосовое.
Работаю в трех режимах:
/rude - грубый режим
/polite - вежливый режим
/guard - молча удаляю все аудиосообщения из чата
(требуются права админа на удаление сообщений)
/rating - доска позора войсеров
Для выбора режима введите соответствующую команду (только админ чата)

Дополнительные настройки:
/hatevideo_on - хейтятся также видеосообщения
/hatevideo_off - хейтятся только аудио (по умолчанию)
"""
SETTINGS = ["rude", "polite", "guard", "hatevideo_on", "hatevideo_off"]

'''
/check - статус настроек
/star or /help - регистрация чата или инфо
Команды управления режимами выше
/features - выводит сообщение с фичами
'''


# Admin actions in a group goes here ...

def get_id(message: types.Message) -> int:
    '''Выбор тип чата и его ИД.
    Возвращает 0, если это не чат или группа'''
    output: int = 0
    if message.chat.type == 'private':
        output = message.chat.id
    elif (message.chat.type == 'group' or
          message.chat.type == 'supergroup'):
        output = message.chat.shifted_id
    return output


# Welcome function
@dp.message_handler(is_admin=True,
                    commands=['start', 'help'],
                    commands_prefix="!/"
                    )
async def send_welcome(message: types.Message):
    """This handler will be called when user
    send `/start` or `/help` command"""

    chat_id = get_id(message)
    if chat_id == 0:
        await message.reply(f'Я не работаю с типом чатов {message.chat.type}.')

    cmd_variants = (('/start', '!start'), ('/help', '!help'))
    # Обработка какая команда нажата
    if message.text.startswith(cmd_variants[0]):
        # Добавляем наш чат в БД, если его там нет.
        # Если есть, ставим настроки по умолчанию
        BotDB.upd_group(chat_id,)
    # Если help то просто выведем подсказку
    await message.reply(WELCOME_TEXT)


@dp.message_handler(is_admin=True,
                    commands="check",
                    commands_prefix="!/"
                    )
async def check(message: types.Message):
    '''Settings check function'''
    chat_id = get_id(message)
    if chat_id == 0:
        await message.reply(f'Я не работаю с типом чатов {message.chat.type}.')
    # SQL DB integration_____________________
    try:
        mode, video = BotDB.get_group_settings(chat_id)
        await message.reply(f"Режим: {mode} \\ Video: {bool(video)}")
    except TypeError:
        await message.answer("Я еще не подключен к вашему чату. "
                             "Выполните /start (админ)")
        return False


@dp.message_handler(is_admin=True,
                    commands=SETTINGS,
                    commands_prefix="!/"
                    )
async def change_settings(message: types.Message):
    '''Settings change function: Mode, Video_hate'''
    chat_id = get_id(message)
    if chat_id == 0:
        await message.reply(f'Я не работаю с типом чатов {message.chat.type}.')

    cmd_variants = (('/rude', '!rude'),
                    ('/polite', '!polite'),
                    ('/guard', '!guard')
                    )
    sub_cmd = (('/hatevideo_on', '!hatevideo_on'),
               ('/hatevideo_off', '!hatevideo_off')
               )
    # set variables with current value
    try:
        act_type = BotDB.get_group_settings(chat_id)[0]
        video_hate = BotDB.get_group_settings(chat_id)[1]
    except TypeError:
        await message.answer("Я еще не подключен к вашему чату. "
                             "Выполните /start (админ)")
        return False
    # Обработка какая команда нажата
    if message.text.startswith(cmd_variants[0]):
        act_type = 'rude'
    elif message.text.startswith(cmd_variants[1]):
        act_type = 'polite'
    elif message.text.startswith(cmd_variants[2]):
        act_type = 'guard'

    # videohate
    if message.text.startswith(sub_cmd[0]):
        video_hate = int(True)
    elif message.text.startswith(sub_cmd[1]):
        video_hate = int(False)

    # SQL DB integration_____________________
    # Выполним изменение настроек в БД
    print(f"LOG: Обновляем настройки группы {chat_id} "
          f"в бд: {BotDB.upd_group(chat_id, act_type, video_hate)}")
    await message.reply(f"Настройки успешно сохранены. "
                        f"Режим: {act_type}, Video: {bool(video_hate)}."
                        )


@dp.message_handler(is_admin=True,
                    commands=["features"],
                    commands_prefix="!/"
                    )
async def annons(message: types.Message):
    '''What's new? Show new features and general info'''
    ver, auth, feature, soon = list(DATABASE['info'].values())
    await message.reply(f"""Версия: {ver}
Автор: {auth}
Что нового:
{feature}
Что ждем:
{soon}
Хочешь предложить фразу или фичу, пиши в лс.""")
