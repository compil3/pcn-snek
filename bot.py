import logging
from logging.handlers import RotatingFileHandler

import dis_snek.const
from dis_snek.models.enums import Intents
from dis_snek.models.listener import listen
from dis_snek.client import Snake

from dotenv import load_dotenv

import os
from os import environ, listdir

from sys import platform

import time
import sys


start = time.perf_counter()


class Bot(Snake):
    def __init__(self):
        super().__init__(
            intents=Intents.ALL,
            default_prefix="?",
            sync_interactions=True,
            delete_unused_application_cmds=True,
            asyncio_debug=True,
            message_cache_ttl=600,
            message_cache_limit=250,
        )

    @listen()
    async def on_ready(self):
        print("Ready")
        if platform == "linux" or platform == "linxu2":
            # os.system("clear")
            print("--Pro Clubs Nation Bot v1.0---")
            print(
                f"Logged in as {await bot.name} ID:{await bot.id} after {round(time.perf_counter() - start, 2)} seconds"
            )
            logging.info(
                f"Logged in as {await bot.name} ID:{await bot.id} after {round(time.perf_counter() - start, 2)} seconds"
            )
        elif platform == "win32":
            # os.system('cls')
            print("--Pro Clubs Nation Bot v1.0---")
            print(
                f"Logged in as {bot.user} ID:{bot.user.id} after {round(time.perf_counter() - start, 1)} seconds"
            )
            logging.info(
                f"Logged in as {bot.user} ID: {bot.user.id} after {round(time.perf_counter() - start, 1)} seconds"
            )


bot = Bot()
print(os.path)
if os.path.exists("./Logs") is False:
    os.makedirs("./Logs")
elif os.path.exists("./Logs/bot.log"):
    os.remove("./Logs/bot.log")
else:
    pass
logging.basicConfig(
    handlers=[
        RotatingFileHandler("./Logs/bot.log", maxBytes=5000000, backupCount=3)
    ],
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)d: %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
)

for filename in listdir("./scales"):
    if filename.endswith(".py") and not filename.startswith("_"):
        try:
            bot.grow_scale(f"scales.{filename[:-3]}")
            print(f"Loaded scales.{filename[:-3]}")
            logging.info(f"scales.{filename[:-3]} loaded.")
        except Exception as e:
            print(f"Failed to load scale {filename[:-3]}.", file=sys.stderr)


load_dotenv()
bot.start(environ.get('TOKEN'))