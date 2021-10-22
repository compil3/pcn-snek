import logging
from re import T
from dis_snek.models.checks import has_role

from dis_snek.models.command import message_command
from dis_snek.models.listener import listen
from extensions import default

import motor.motor_asyncio as motor

from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (
    Permission,
    slash_command,
    slash_option,
    slash_permission,
)
from dis_snek.models.command import (
    message_command
)
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.discord_objects.guild import GuildWelcome, GuildWelcomeChannel


from datetime import datetime
from dotenv import load_dotenv
from os import environ

import re
from extensions import default
load_dotenv(".env")


config = default.config()
# default_player_url = config['urls']['players']

# Mongo stuff
cluster = motor.AsyncIOMotorClient(f"{environ.get('CONNECTION')}")
db = cluster["Nation"]
collection = db["registered"]

guild_id = 689119429375819951

# New role - 843896103686766632
# Player role - 843899510483976233
admin_perm = [Permission(843896103686766632, 1, True)]
register = Permission(843896103686766632,1,True),Permission(842505724458172467,1,True)

format = "%b %d %Y %I:%M%p"


class Register(Scale):

    @slash_command(
        "register",
        description="Register Discord to your Gamertag.**HINT** Look at your player profile page url.('-' FOR SPACES)",
        scope=guild_id,
        default_permission=False
    )
    @slash_permission(guild_id=guild_id, permissions=register)
    @slash_option("gamertag", "Xbox Gamertag", 3, required=True, choices=None)
    async def register(self, ctx, gamertag: str):
        _status = None

        if bool(re.search(r"\s", gamertag)):
            gamertag = gamertag.replace(" ", "-")

        exists = await collection.find_one({"_id": ctx.author.user.id})

        if exists is not None:
            _status = f"You have already registered a Gamertag.  If you are attempting to change your registered tag, please use ``/reset [new_gamer_tag]``"
            registered_Tag = exists["registered_gamer_tag"]
            date_registered = exists["date_registered"]
        else:
            current_time = datetime.now()
            reg_date = current_time.strftime(format)
            post = {
                "_id": ctx.author.id,
                "discord_full_name": ctx.author.user.display_name
                + "#"
                + ctx.author.user.discriminator,
                "registered_gamer_tag": gamertag,
                "gamer_tag_url": config['urls']['players'].format(gamertag),
                "date_registered": reg_date,
            }
            await collection.insert_one(post)
            _status = f"Gamertag successfully registered."
        embed = Embed(title="PCN Discord Registration System", description=_status)
        embed.add_field(
            name="Gamertag", value=exists["registered_gamer_tag"], inline=False
        )
        embed.add_field(
            name="Registration Date", value=exists["date_registered"], inline=False
        )
        embed.set_author(
            name=f"{exists['registered_gamer_tag']} Link",
            url=config['urls']['players'].format(gamertag),
            icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
        )

        await ctx.send(embeds=[embed], ephemeral=True)

    
    async def on_command_error(self, e, *args, **kwargs):
        print(f"{args=}")




def setup(bot):
    Register(bot)
