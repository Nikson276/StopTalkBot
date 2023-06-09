"""_summary_
Для использования dotenv нужно убедиться, что установлен модуль python-dotenv

Данный файл конфигурации позволяет при локальном запуске в режиме разработки, 
запускать бота с одними значениями (из файла dev.env).

А когда проект будет размещен на сервере, этот файл не понадобиться.
Вместо него необходимо добавить в вирт окружение необходимые переменные
'BOT_TOKEN' = <значение> без ковычек
'BOT_OWNERS' = <значение> без ковычек.
"""

from dotenv import load_dotenv
import os

# Find .env file with os variables
load_dotenv("dev.env")

# retrieve config variables
try:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_OWNERS = [int(x) for x in os.getenv('BOT_OWNERS').split(",")]
except (TypeError, ValueError) as ex:
    print("Error while reading config:", ex)
