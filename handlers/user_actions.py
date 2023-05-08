from random import choice
from aiogram import types
from dispatcher import dp
import db

""" 
Работаю в трех режимах:
/rude - грубый режим
/polite - вежливый режим
/guard - молча удаляю все аудиосообщения из чата (требуются права админа на удаление сообщений)

Comming soon features:
/rating - доска позора войсеров (требует БД)
Для выбора режима введите соответствующую команду (только админ чата)

Дополнительные настройки:
/hatevideo_on - хейтятся также видеосообщения
/hatevideo_off - хейтятся только аудио (по умолчанию)
"""

# User actions in a group goes here ...


#catch voice message
@dp.message_handler(content_types=['voice'])
async def voice_handler(message: types.Voice):
    #default
    mode = db.DATABASE["settings"]["mode"]
    
    #Условие на функцию удаления сообщений
    if mode == 'guard':
        user = message.from_user.username
        await message.delete()
        await message.answer(f"Voice от @{user} удалено.")
        
    else:
        catatog = db.DATABASE["navigator"][mode]            #mode = ключу нужного указателя на словарь
        
        #получим список ответов, и выберем случайное
        text = choice(list(db.DATABASE[catatog].values()))

        #ответим в чат
        await message.reply(text)   
