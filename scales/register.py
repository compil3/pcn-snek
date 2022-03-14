import logging
from re import T
from typing import TYPE_CHECKING
from dis_snek.models.snek.checks import has_role

from dis_snek.models.snek.command import message_command
from dis_snek.models.snek.listener import listen
from extensions import default

from motor import motor_asyncio

from dis_snek.models import Scale
from dis_snek.models.snek.application_commands import (
    Permission,
    PermissionTypes,
    slash_command,
    slash_option,
    slash_permission,
)
from dis_snek.models.snek.command import message_command
from dis_snek.models.discord.embed import Embed
from dis_snek.models.discord.guild import GuildWelcome, GuildWelcomeChannel


from datetime import datetime
from dotenv import load_dotenv
from os import environ

import re
from extensions import default

from pydantic import Field
from beanie import Document, Indexed, init_beanie

if TYPE_CHECKING:
    from main import Bot

load_dotenv(".env")


config = default.get_config()
format = "%b %d %Y %I:%M%p"

class UserRegistration(Document):
    user_id: int
    discord_full_name: str
    registered_gamer_tag: str
    pcn_url: str
    registered_date: str

    class Collection:
        name = "discord_registered"

class Register(Scale):
    @slash_command(
        "signup",
        sub_cmd_name='register',
        sub_cmd_description="Register your discord name to your Xbox Gamertag.", 
        scopes=[689119429375819951,],
        permissions=[Permission(
                843896103686766632, 689119429375819951, PermissionTypes.ROLE, True
            ),
        ],
    )
    @slash_option("gamertag", "Xbox Gamertag", 3, required=True, choices=None)
    async def signup(self, ctx, gamertag: str):
        await ctx.defer(ephemeral=True)

        _registration_tag = None
        _registration_date = None
        embed = None

        if bool(re.search(r"\s", gamertag)):
            gamertag = gamertag.replace(" ", "-")
        
        find_user = await UserRegistration.find_one(UserRegistration.user_id == ctx.author.id)

        if find_user is not None:
            _registration_tag = find_user.registered_gamer_tag
            _registration_date = find_user.registered_date 
            embed = Embed(
                title=":warning: Registration unsuccessful",
                description=f"The following gamertag has already been registered for this discord user:\n\n **{gamertag}** \n\nIf you are attempting to change your registered tag, please use ``/reset [new_gamer_tag]``"
            )
            embed.add_field("PCN Profile", f"[Link](https://proclubsnation.com/player/{gamertag})", inline=False)
        else:
            registering_user = UserRegistration(
                user_id = ctx.author.id,
                discord_full_name = ctx.author.user.display_name + "#" + ctx.author.user.discriminator,
                registered_gamer_tag=gamertag,
                pcn_url=config["urls"]["players"].format(gamertag),
                registered_date=datetime.now().strftime(format),
            )
            await registering_user.save()
            _registration_tag = registering_user.registered_gamer_tag
            _registration_date = registering_user.registered_date
            embed = Embed(
                title=f":white_check_mark: Registration successful",
                description=f"Here are your registration details *{ctx.author.display_name}*"
            )
            
        embed.add_field(
            name="Registered Gamertag", value=_registration_tag, inline=False
        )
        embed.add_field(
            name="Registration Date", value=_registration_date, inline=False
        )
        embed.add_field("PCN Profile", f"[Link](https://proclubsnation.com/player/{gamertag})", inline=False)

        embed.set_author(
            name=f"PCN Discord Registration System",
            # url=f"https://proclubsnation.com",
            icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
        )
        await ctx.send(embeds=[embed])

    @signup.subcommand(
       "change", sub_cmd_description="Change your registered gamertag"
    )
    @slash_option("gamertag", "Xbox Gamertag", 3, required=True, choices=None)
    async def changetag(self, ctx, new_tag: str):
        await ctx.defer(ephemeral=True)
        embed = None
        if bool(re.search(r"\s", new_tag)):
            new_tag = new_tag.replace(" ", "-")

        try:
            find_user = await UserRegistration.find_one(UserRegistration.user_id == ctx.author.id)
        except Exception as e:
            logging.error(e)
            await ctx.send("An error occurred, please try again later.")

        if find_user is not None:
            find_user.registered_gamer_tag = new_tag
            find_user.registered_date =  datetime.now().strftime(format)

            try:
                await find_user.save()
            except Exception as e:
                await ctx.send("Unable to update your gamertag. Please try again later.")
            
            embed = Embed(
                title=":white_check_mark: Gamertag change was successful",
                description=f"Here are the details *{ctx.author.display_name}*"
            )
            embed.add_field(
                name="New registered Gamertag", value=find_user.registered_gamer_tag, inline=False
            )
            embed.add_field(
                name="Update Date", value=find_user.registered_date, inline=False
            )
            embed.add_field("PCN Profile", f"[Link](https://proclubsnation.com/player/{new_tag})", inline=False)

            embed.set_author(
                name=f"PCN Discord Registration System",
                # url=f"https://proclubsnation.com",
                icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
            )
            await ctx.send(embeds=[embed])            
        else:
            await ctx.send(f"You have not registered your gamertag yet. Please use ``/signup [gamertag]``")



def setup(bot):
    Register(bot)
    bot.add_model(UserRegistration)
