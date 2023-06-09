import logging
from aiogram import Bot, Dispatcher, types
from filters import IsOwnerFilter, IsAdminFilter    #, MemberCanRestrictFilter
import config


#log level 
logging.basicConfig(level=logging.INFO)

# prerequisites
if not config.BOT_TOKEN:
    exit("No token provided")

# init
# PROXY_URL = "http://proxy.server:3128"
# bot = Bot(proxy=PROXY_URL, token=config.BOT_TOKEN, parse_mode="HTML")
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
# dp.filters_factory.bind(MemberCanRestrictFilter)
