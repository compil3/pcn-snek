import asyncio
import logging
import os
from http.client import HTTPException
from pathlib import Path
from sys import platform
from typing import Optional

from beanie import init_beanie
from motor import motor_asyncio
from naff import (AllowedMentions, Client, Intents, InteractionContext, errors,
                  listen)
from naff.models.naff.context import Context
import utils.log as log_utils
from config import ConfigLoader
from loguru import logger

# logger: log_utils.BotLogger = logging.getLogger()
dev = False

logger.add("./logs/main.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level="INFO", rotation="50 MB", retention="5 days", compression="zip")


class Bot(Client):

    @logger.catch
    def __init__(self, current_dir, config):
        self.current_dir: Path = current_dir
        self.config = config

        super().__init__(
            intents=Intents.DEFAULT | Intents.GUILD_MEMBERS,
            sync_interactions=True,
            asyncio_debug=False,
            delete_unused_application_cmds=True,
            activity="PCN Test Flight",
        )

        self.db: Optional[motor_asyncio.AsyncIOMotorClient] = None
        self.models = list()

    @logger.catch
    def get_extension(self):
        logger.info("Loading Extensions...")

        # go through all folders in the directory and load the extensions from all files
        # Note: files must end in .py
        for root, dirs, files in os.walk("extensions"):
            for file in files:
                if file.endswith(".py") and not file.startswith("__init__") and not file.startswith("__"):
                    file = file.removesuffix(".py")
                    path = os.path.join(root, file)
                    python_import_path = path.replace("/", ".").replace("\\", ".")
                    # print(python_import_path)
                    # load the extension
                    self.load_extension(python_import_path)

    @logger.catch
    async def startup(self):
        self.get_extension()
        if dev:
            self.grow_scale("dis_snek.ext.debug_scale")

        self.db = motor_asyncio.AsyncIOMotorClient(self.config.database_address)
        await init_beanie(database=self.db.Nation, document_models=self.models)
        if self.config.debug is True:
            await self.astart(self.config._dev_token)
        else:
            await self.astart(self.config.discord_token)
    
    @listen()
    async def on_ready(self):
        msg = f"Logged in as {self.user}.\nCurrent scales: {', '.join(self.ext)}"

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # os.system("clear")
            print(f"--Pro Clubs Nation Bot {self.config.version}")
            print("Connected to {} guild(s)".format(len(self.guilds)))
            # print(msg)
            logger.info(msg)
        elif platform == "win32":
            # os.system('cls')
            logger.info(f"--Pro Clubs Nation Bot {self.config.version}")
            logger.info("Connected to {} guild(s)".format(len(self.guilds)))
            # print(msg)
            logger.info(f"Logged in as {self.user}.")
            logger.info(f"Extensions: {', '.join(self.ext)}")

    async def on_command_error(self, ctx: InteractionContext, error: Exception, *args, **kwargs):
        unexpected = True
        if isinstance(error, errors.CommandCheckFailure):
            unexpected = False
            await send_error(ctx, "Command check failed!\nSorry, but it looks like you don't have permission to use this commands.")
        else:
            await send_error(ctx, str(error)[:2000] or "<No exception text available>")

        if unexpected:
            logger.error(f"Exception during command execution: {repr(error)}", exc_info=error)

    async def on_command(self, ctx: Context):
        _command_name = ctx.invoke_target
        logger.info(f"{ctx.author.display_name} used Command: '{ctx.invoke_target} {ctx.args}'")

    async def on_error(self, source: str, error: Exception, *args, **kwargs) -> None:
        """Bot on_error override"""
        if isinstance(error, HTTPException):
            errors = error.search_for_message(error.errors)
            out = f"HTTPException: {error.status}|{error.response.reason}: " + "\n".join(errors)
            logger.error(out, exc_info=error)
        else:
            logger.error(f"Ignoring exception in {source}", exc_info=error)

    def add_model(self, model):
        self.models.append(model)

@logger.catch
async def send_error(ctx, msg):
    if ctx is not None:
        await ctx.send(msg, allowed_mentions=AllowedMentions.none(), ephemeral=True)
    else:
        logger.warning(f"Already responded to message, error message: {msg}")


@logger.catch
def main():
    current_dir = Path(__file__).parent
    print(current_dir)
    config = ConfigLoader.load_settings()
    # TODO: Move cache config here to set it once and to be called self.bot.cache_config()
    # if os.path.exists("cache.db"):
    #     os.remove("cache.db")

    # log_level = logging.DEBUG if dev else logging.INFO

    # logs_dir = current_dir / "logs"
    # log_utils.configure_logging(logger, logs_dir, log_level)


    bot = Bot(current_dir, config)
    asyncio.run(bot.startup())


if __name__ == "__main__":
    main()
