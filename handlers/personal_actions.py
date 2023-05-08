from aiogram import types
from dispatcher import dp
from db import settings_upd, read


# Personal actions goes here (bot direct messages)
# Here is some example !ping command ...
@dp.message_handler(is_owner=True, commands="ping", commands_prefix="!/")
async def cmd_ping_bot(message: types.Message):
    await message.reply("<b>👊 Ping & Ping!</b>\n Owner is here\n")

