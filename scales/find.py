from datetime import datetime

import motor.motor_asyncio as motor
import requests
from dis_snek.models.snek.application_commands import PermissionTypes

from dis_snek.models import (
    Embed,
    Permission,
    Scale,
    context_menu,
    slash_command,
    slash_option,
    slash_permission,
    MaterialColors,
    Permissions,
)
from dis_snek.models.snek.context import InteractionContext
from dis_snek.models.discord.enums import CommandTypes
from beanie import Document
from dotenv import load_dotenv
from extensions import default
from config import load_settings

load_dotenv()
config = default.get_config()
default_player_url = config["urls"]["find_player"]

guild_id = 689119429375819951
admin_perm = [Permission(842505724458172467, 1, True)]


# TODO: Add guild ids to a json config file instead of hardcoring them
# TODO: Make the data retrieval async in all user facing commands


class Registered(Document):
    user_id: int
    discord_full_name: str
    registered_gamer_tag: str
    pcn_url: str
    registered_date: str

    class Collection:
        name = "discord_registered"

class PlayerFinder(Scale):

    def __init__(self, bot):
        self.bot = bot
        self.config = load_settings()
        # config = self.config

    
    def D_Embed(self, title: str) -> Embed:
        e = Embed(
            f"PCN Player Lookup: {title}",
            color=MaterialColors.BLUE_GREY,
            timestamp=datetime.now(),
        )
        e.set_footer(
            "proclubsnation.com",
            icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
        )
        return e

    @slash_command("find", "Staff only",
        scopes=[
            689119429375819951,442081251441115136
        ],
        default_permission=True,
    )
    @slash_permission(
        # Permission(910676210172977213, 174342051318464512, PermissionTypes.ROLE, True),  # Player, TheNine
        # Permission(442081251441115136, 449043802829750272,  PermissionTypes.ROLE, True), # Player, PCN Discord
        Permission(442081251441115136, 608012366197686286, PermissionTypes.ROLE, True), # Moderator, PCN Discord)      
    )
    # @slash_permission(guild_id=guild_id, permissions=admin_perm)
    @slash_option("gamertag", "Enter Gamertag to check", 3, required=True)
    async def find(self, ctx: InteractionContext, gamertag: str):
        """Finds a player using /find [gamertag]"""
        # await ctx.send(f"Searching for {gamertag}...", ephemeral=True)
        await ctx.defer(ephemeral=True)
        # try:
        url = self.config.urls.find_player.format(f"{gamertag}&_fields=title,link,date,modified,slug")
        try:
            r = requests.get(url)
            if r.status_code == 200:
                if r.json()[0] is None:
                    raise IndexError
                else:
                    e = self.D_Embed(
                        f"**{r.json()[0]['title']['rendered']}**"
                    )
                    e.add_field(
                        "Registered", r.json()[0]["date"], inline=True
                    )
                    e.add_field(
                        "Last Updated", r.json()[0]["modified"], inline=True
                    )
                    e.add_field("Slug", r.json()[0]["slug"])
                    e.add_field("PCN Profile", r.json()[0]["link"])
                    await ctx.send(embeds=[e])
            else:
                e = self.D_Embed(f"Connection Error")
                e.description = "Failed to connect to API.\n\n{e}\n\nTry again later."
                await ctx.send(embeds=[e])
        except IndexError:
            e = self.D_Embed(f"Results")
            e.description = f"**{gamertag}** not found"
            await ctx.send(embeds=[e])


    #TODO Use the register command to add users to database.  Then pull the gamer tag from the database and use it to find the player.
    @context_menu("Search",CommandTypes.USER,scopes=[689119429375819951,442081251441115136])
    @slash_permission(
        # Permission(910676210172977213, 174342051318464512, PermissionTypes.ROLE, True),  # Player, TheNine
        # Permission(442081251441115136, 449043802829750272,  PermissionTypes.ROLE, True), # Player, PCN Discord
        Permission(442081251441115136, 608012366197686286, PermissionTypes.ROLE, True), # Moderator, PCN Discord)      
    )
    async def search(self, ctx: InteractionContext):
        """
        Finds selected player when right clicking>Apps>Lookup
        """
        await ctx.defer(ephemeral=True)

        member = self.bot.get_member(ctx.target_id, ctx.guild_id)
        try:
            find_user = await Registered.find_one(Registered.user_id == member.id)
            if find_user is None:
                raise IndexError
            r = requests.get(self.config.urls.find_player.format(f"{find_user.registered_gamer_tag}&_fields=title,link,date,modified,slug"))
            if r.status_code == 200:
                if r.json()[0] is None:
                    raise IndexError
                else:
                    e = self.D_Embed(
                        f"**{r.json()[0]['title']['rendered']}**"
                    )
                    e.add_field("Registered GT", find_user.registered_gamer_tag, inline=False)
                    e.add_field("Discord ID", str(member))
                    e.add_field(
                        "Registation Date", r.json()[0]["date"], inline=False
                    )
                    e.add_field(
                        "Last Updated", r.json()[0]["modified"], inline=False
                    )
                    e.add_field("API Slug", r.json()[0]["slug"])
                    e.add_field("PCN Profile", r.json()[0]["link"])
                    await ctx.send(embeds=[e])
            else:
                e = self.D_Embed(f"Connection Error")
                e.description = "Failed to connect to API.\n\n{e}\n\nTry again later."
                await ctx.send(embeds=[e])
        except IndexError:
            e = self.D_Embed(f"Results")
            e.description = f"**{member}** is not registered with Bot."
            # e.add_field("Registered GT", "Not Registered with Bot", inline=False)
            await ctx.send(embeds=[e])


def setup(bot):
    PlayerFinder(bot)
    bot.add_model(Registered)
