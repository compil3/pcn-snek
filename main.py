# TODO: add team role assignment, check player site for current team and if react-team matchs, add role, if not do nothing, also rate-limit.
import asyncio
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from sys import platform
from typing import Optional


from beanie import init_beanie
from motor import motor_asyncio
from naff import (AllowedMentions, Client, Intents, InteractionContext, errors,
                  listen, logger_name)

from config import ConfigLoader

import utils.log as log_utils

logger: log_utils.BotLogger = logging.getLogger()
dev = True


class Bot(Client):
    def __init__(self, current_dir, config):
        self.current_dir: Path = current_dir
        self.config = config

        super().__init__(
            intents=Intents.DEFAULT | Intents.GUILD_MEMBERS,
            sync_interactions=True,
            auto_defer=True,
            asyncio_debug=self.config.debug,
            delete_unused_application_cmds=True,
            activity="PCN Test Flight",
        )

        self.db: Optional[motor_asyncio.AsyncIOMotorClient] = None
        self.models = list()

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

                    # load the extension
                    self.load_extension(python_import_path)

    async def startup(self):
        self.get_extension()
        if self.config.debug:
            self.grow_scale("dis_snek.ext.debug_scale")

        self.db = motor_asyncio.AsyncIOMotorClient(self.config.database_address)
        await init_beanie(database=self.db.Nation, document_models=self.models)
        if dev is True:
            await self.astart(self.config._dev_token)
        else:
            await self.astart(self.config.discord_token)

    @listen()
    async def on_ready(self):
        msg = f"Logged in as {self.user}.\nCurrent scales: {', '.join(self.ext)}"

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # os.system("clear")
            print("--Pro Clubs Nation Bot v1.0---")
            # print(msg)
            logger.info(msg)
        elif platform == "win32":
            # os.system('cls')
            print("--Pro Clubs Nation Bot v1.0---")
            # print(msg)
            logger.info(msg)

    async def on_command_error(self, ctx: InteractionContext, error: Exception, *args, **kwargs):
        unexpected = True
        if isinstance(error, errors.CommandCheckFailure):
            unexpected = False
            await send_error(ctx, "Command check failed!\nSorry, but it looks like you don't have permission to use this commands.")
        else:
            await send_error(ctx, str(error)[:2000] or "<No exception text available>")

        if unexpected:
            logger.error(f"Exception during command execution: {repr(error)}", exc_info=error)

    def add_model(self, model):
        self.models.append(model)


async def send_error(ctx, msg):
    if ctx is not None:
        await ctx.send(msg, allowed_mentions=AllowedMentions.none(), ephemeral=True)
    else:
        logger.warning(f"Already responded to message, error message: {msg}")


def main():
    current_dir = Path(__file__).parent
    config = ConfigLoader.load_settings()

    log_level = logging.DEBG if config.debug else logging.INFO

    logs_dir = current_dir / "logs"
    log_utils.configure_logging(logger, logs_dir, log_level)

    # sentry_sdk.init(config.sentry_token)
    # division_by_zero = 1 / 0

    # current_dir = Path(__file__).parent
    # logs_dir = current_dir / "Logs"
    # if not os.path.exists(logs_dir):
    #     os.mkdir(logs_dir)

    # handlers = [
    #     TimedRotatingFileHandler(logs_dir / f"bot.log", when="W0", encoding="utf-8"),
    #     logging.StreamHandler(),
    # ]

    # log_level = logging.DEBUG if config.debug else logging.INFO
    # formatter = logging.Formatter("[%(asctime)s] [%(levelname)-9.9s]-[%(name)-15.15s]: %(message)s")
    
    # # logging.setLoggerClass(log_utils.BotLogger)
    # snek_logger = logging.getLogger(logger_name)
    # snek_logger.setLevel(log_level)
    # logger.setLevel(log_level)

    # for handler in handlers:
    #     handler.setFormatter(formatter)
    #     snek_logger.addHandler(handler)
    #     logger.addHandler(handler)

    bot = Bot(current_dir, config)
    asyncio.run(bot.startup())


if __name__ == "__main__":
    main()