from aiogram import types
from dispatcher import dp
import db

"""
Работаю в трех режимах:
/rude - грубый режим
/polite - вежливый режим
/guard - молча удаляю все аудиосообщения из чата (требуются права админа на удаление сообщений)
/rating - доска позора войсеров
Для выбора режима введите соответствующую команду (только админ чата)

Дополнительные настройки:
/hatevideo_on - хейтятся также видеосообщения
/hatevideo_off - хейтятся только аудио (по умолчанию)
"""

welcome_text = """
Приветствую! Я бот для чатов, ругаюсь в ответ на аудиосообщения.\n
Собственно, пока это всё.\n
Если у вас не в почете людишки, записывающие аудио, смело добавляйте меня в чат.\n
Если хочешь проверить, просто отправь мне голосовое.
"""

# Admin actions in a group goes here ...
   

# Welcome function
@dp.message_handler(is_admin=True, commands=['start', 'help'], commands_prefix="!/")
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(welcome_text)

#check mode
@dp.message_handler(is_admin=True, commands="check", commands_prefix="!/")
async def check(message: types.Message):
    #получим список ответов
    # values = list(db.DATABASE["settings"].items())
    mode = db.DATABASE["settings"]["mode"]
    video = db.DATABASE["settings"]["hate_video"]
    await message.reply(f"MODE= {mode} \ Video: {video}")
    # print("СЛОВАРЬ выглядит так: ", values)
    
#change settings "Mode"
@dp.message_handler(is_owner=True, commands=["rude", "polite", "guard"], commands_prefix="!/")
async def cmd_chg_mode(message: types.Message):
    cmd_variants = (('/rude', '!rude'), ('/polite', '!polite'), ('/guard', '!guard'))
    #Обработка какая команда нажата
    if message.text.startswith(cmd_variants[0]):
        act_type = 'rude'
    elif message.text.startswith(cmd_variants[1]):
        act_type = 'polite'
    elif message.text.startswith(cmd_variants[2]):
        act_type = 'guard'
    
    #запустим обновление настроек с помощью функции:
    if db.settings_upd("mode", act_type):
        await message.reply(f"Изменение MODE={act_type} выполнено успешно.")
    else:
        await message.reply("ОШИБКА при изменении MODE.")