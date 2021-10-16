import logging
from re import T
import motor.motor_asyncio as motor

from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (Permission, slash_command, slash_option, slash_permission)
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.context import InteractionContext




from datetime import datetime
from dotenv import load_dotenv
from os import environ

import re

load_dotenv('.env')
default_player_url = "https://proclubsnation.com/wp-json/sportspress/v2/players?slug={}"

# Mongo stuff
cluster = motor.AsyncIOMotorClient(f"{environ.get('CONNECTION')}")
db = cluster["Nation"]
collection = db["registered"]

guild_id = 689119429375819951
admin_perm = [Permission(843899510483976233,1,True)]
format = "%b %d %Y %I:%M%p"


class Register(Scale):

    @slash_command("register", description="Register Discord to your Gamertag.**HINT** Look at your player profile page url.('-' FOR SPACES)", scope=guild_id)
    @slash_permission(guild_id=guild_id, permissions=admin_perm)
    @slash_option("gamertag", "Xbox Gamertag", 3, required=True, choices=None)
    async def register(self, ctx, gamertag: str):
        _status = None

        print(dir(ctx))
        print(f"\n\n{dir(ctx.message)}")
        print(f"\n\n{dir(ctx.send)}")

        if bool(re.search(r"\s", gamertag)):
            gamertag = gamertag.replace(" ","-")

        exists = await collection.find_one({"_id": ctx.author.user.id})

        if exists is not None:
            _status = f"You have already registered a Gamertag.  If you are attempting to change your registered tag, please use ``/reset [new_gamer_tag]``"
            # embed.set_author(name=f"{exists['registered_gamer_tag']} Link", url=default_player_url.format(gamertag), icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png")
            # embed.add_field(name="Gamertag", value=exists['registered_gamer_tag'], inline=False)
            # embed.add_field(name="Registered On", value=exists['date_registered'], inline=False)
            # await ctx.send(f"{ctx.author.user.mention} Check your DMs.", ephemeral=True)

            # await ctx.author.user.send(embeds=[embed], ephemeral=True)
        else:
            current_time = datetime.now()
            reg_date = current_time.strftime(format)
            post = {
                "_id": ctx.author.id,
                "discord_full_name": ctx.author.user.display_name + "#" + ctx.author.user.discriminator,
                "registered_gamer_tag": gamertag,
                "gamer_tag_url": default_player_url.format(gamertag),
                "date_registered": reg_date
            }
            await collection.insert_one(post)
            _status = f"Gamertag successfully registered."
        embed = Embed(title="PCN Discord Registration System", description=_status)
        embed.set_author(name=f"{exists['registered_gamer_tag']} Link", url=default_player_url.format(gamertag), icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png")
        embed.add_field(name="Gamertag", value={exists['registerd_gamer_tag']}, inline=False)
        embed.add_field(name="Registration Date", value=reg_date, inline=False)
        await ctx.send(f"{ctx.author.user.mention} Check your DMs.", ephemeral=True)
        await ctx.author.send(embeds=[embed], ephemeral=True)


    @register.error
    async def command_error(self, e, *args, **kwargs):
        print(f"{e}\n\n")
     

def setup(bot):
   Register(bot) 