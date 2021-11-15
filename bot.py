import logging
import os
import sys
import time
import zoneinfo
from logging.handlers import RotatingFileHandler
from os import listdir
from sys import platform

from dis_snek.client import Snake
from dis_snek.errors import ScaleLoadException
from dis_snek.models import Activity, ActivityType
from dis_snek.models.enums import Intents
from dis_snek.models.listener import listen
from dotenv import load_dotenv


from extensions import default

start = time.perf_counter()

config = default.get_config()
time_seconds = 0
time_minutes = 0
time_hours = 0
time_days = 0
Toronto = zoneinfo.ZoneInfo('America/Toronto')

# logging.basicConfig(filename="logs.log")
# cls_log = logging.getLogger(dis_snek.const.logger_name)
# cls_log.setLevel(logging.DEBUG)


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
        await self.change_presence(
            activity=Activity(
                type=ActivityType.PLAYING,
                name="Powered by Sneks.",
            )
        )
        print(f"{self.user} is ready!")
        print("Ready")
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            os.system("clear")
            print("--Pro Clubs Nation Bot v1.0---")
            print(
                f"Logged in as {bot.user} ID:{bot.user.id} after {round(time.perf_counter() - start, 2)} seconds"
            )
            logging.info(
                f"Logged in as {bot.user} ID:{bot.user.id} after {round(time.perf_counter() - start, 2)} seconds"
            )
        elif platform == "win32":
            os.system('cls')
            print("--Pro Clubs Nation Bot v1.0---")
            print(
                f"Logged in as {bot.user} ID:{bot.user.id} after {round(time.perf_counter() - start, 1)} seconds"
            )
            logging.info(
                f"Logged in as {bot.user} ID: {bot.user.id} after {round(time.perf_counter() - start, 1)} seconds"
            )
        # globals.init()


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


scale_dir = listdir("./scales")
scale_dir = [f.lower() for f in scale_dir]
for filename in sorted(scale_dir):
    try:

        match filename.endswith(".py") and not filename.startswith("_"):
            case True:
                bot.grow_scale(f"scales.{filename[:-3]}")
                logging.info(f"Loaded scales.{filename[:-3]}")
            case False:
                pass

    except ScaleLoadException as e:
        logging.ERROR(f"Failed to load scale {filename[:-3]}.", file=sys.stderr)
        logging.ERROR(e)


load_dotenv()       
bot.start(config['token'])
