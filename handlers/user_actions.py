from random import choice
from aiogram import types
from dispatcher import dp
from db import DATABASE
from bot import BotDB
from handlers.admin_actions import get_id, WELCOME_TEXT


# User actions in a group goes here ...
# Helper function to get settings
def get_mode(message, video=False) -> tuple:
    '''Проверка типа чата и выбор его настроек и id'''
    chat_id = get_id(message)
    # распаковка кортежа, возвращенного из метода в переменные
    try:
        mode = BotDB.get_group_settings(chat_id)[0]
        video = BotDB.get_group_settings(chat_id)[1]
        return (mode, video, chat_id)
    except TypeError:
        print('Error. Бот не инициализирован. Выполните команду /start')
        return None


@dp.message_handler(commands="echo", commands_prefix="!/")
async def echo(message: types.Message):
    ''' Here is some example !ping command ...'''
    await message.reply('Проверка связи, Привет Мир!')


# Welcome function
@dp.message_handler(commands=['help'],
                    commands_prefix="!/"
                    )
async def send_welcome(message: types.Message):
    """This handler will be called when user
    send `/help` command"""

    chat_id = get_id(message)
    if chat_id == 0:
        await message.reply(f'Я не работаю с типом чатов {message.chat.type}.')
        return False
    await message.reply(WELCOME_TEXT)


@dp.message_handler(content_types=['voice'])
async def voice_handler(message: types.Voice):
    '''The main func - Catching all voice messages'''
    # SQL DB integration_____________________
    try:
        mode, z, chat_id = get_mode(message)
    except TypeError:
        await message.answer("Я еще не подключен к вашему чату. "
                             "Выполните /start (админ)")
        return False
    # Условие на функцию удаления сообщений
    if mode == 'guard':
        user = message.from_user.username
        await message.delete()
        await message.answer(f"Voice от @{user} удалено.")

    else:
        # mode = ключу нужного указателя на словарь
        catatog = DATABASE["navigator"][mode]

        # получим список ответов, и выберем случайное
        text = choice(list(DATABASE[catatog].values()))

        # ответим в чат
        await message.reply(text)

    # Запись в доску позора (Рейтинг)
    BotDB.upd_user_rating(chat_id, message.from_id, rate='voice_score')


@dp.message_handler(content_types=['video_note'])
async def video_handler(message: types.VideoNote):
    '''The additioan func - Catch all VideoNote messages'''

    try:
        mode, video_hate, chat_id = get_mode(message)
    except TypeError:
        await message.answer("Я еще не подключен к вашему чату. "
                             "Выполните /start (админ)")
        return False

    # Условие на функцию удаления сообщений
    if video_hate:
        key = 'video_' + mode
        catatog = DATABASE["navigator"][key]

        # получим список ответов, и выберем случайное
        text = choice(list(DATABASE[catatog].values()))        
        await message.reply(text)
        # Запись в доску позора (Рейтинг)
        BotDB.upd_user_rating(chat_id, message.from_id, rate='video_score')
