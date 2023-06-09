from aiogram import types
from dispatcher import dp
from bot import BotDB


# Personal actions goes here (bot direct messages)

@dp.message_handler(is_owner=True, commands="ping", commands_prefix="!/")
async def cmd_ping_bot(message: types.Message):
    '''Here is some example !ping command ...'''
    await message.reply("<b>👊 Ping & Ping!</b>\n Owner is here\n Personal act")


@dp.message_handler(is_owner=True, commands="check", commands_prefix="!/")
async def check(message: types.Message):
    '''Settings check function'''
    # Выбор тип чата и его ИД
    if message.chat.type == 'private':
        chat_id = message.chat.id
    elif (message.chat.type == 'group' or
          message.chat.type == 'supergroup'):
        chat_id = message.chat.shifted_id

    # SQL DB integration_____________________
    try:
        mode, video = BotDB.get_group_settings(chat_id)
        await message.reply(f"Режим: {mode} \\ Video: {bool(video)}")
    except TypeError:
        await message.answer("Я еще не подключен к вашему чату. "
                             "Выполните /start (админ)")
        return False
