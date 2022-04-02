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


class PlayerFinder(Scale):
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
        await ctx.send(f"Searching for {gamertag}...", ephemeral=True)
        # try:
        url = default_player_url.format(gamertag)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                if r.json()[0] is None:
                    raise IndexError
                else:
                    player_found = requests.get(
                        config["urls"]["find_player"].format(
                            f"{gamertag}&_fields=title,link,date,modified,slug"
                        )
                    )
                    e = self.D_Embed(
                        f"**{player_found.json()[0]['title']['rendered']}**"
                    )
                    e.add_field(
                        "Registered", player_found.json()[0]["date"], inline=True
                    )
                    e.add_field(
                        "Last Updated", player_found.json()[0]["modified"], inline=True
                    )
                    e.add_field("Slug", player_found.json()[0]["slug"])
                    e.add_field("PCN Profile", player_found.json()[0]["link"])
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
    @context_menu(
        "Search",
        CommandTypes.USER,
        scopes=[
            689119429375819951,442081251441115136
        ],        
    )
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
        print(str(member.display_name))
        url = default_player_url.format(member.display_name)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                if r.json()[0] is None:
                    raise IndexError
                else:
                    player_found = requests.get(
                        config["urls"]["find_player"].format(
                            f"{member.display_name}&_fields=title,link,date,modified,slug"
                        )
                    )
                    e = self.D_Embed(
                        f"**{player_found.json()[0]['title']['rendered']}**"
                    )
                    e.add_field("Discord ID", str(member))
                    e.add_field(
                        "Registered", player_found.json()[0]["date"], inline=True
                    )
                    e.add_field(
                        "Last Updated", player_found.json()[0]["modified"], inline=True
                    )
                    e.add_field("Slug", player_found.json()[0]["slug"])
                    e.add_field("PCN Profile", player_found.json()[0]["link"])
                    await ctx.send(embeds=[e])
            else:
                e = self.D_Embed(f"Connection Error")
                e.description = "Failed to connect to API.\n\n{e}\n\nTry again later."
                await ctx.send(embeds=[e])
        except IndexError:
            e = self.D_Embed(f"Results")
            e.description = f"**{member}** not found"
            await ctx.send(embeds=[e])


def setup(bot):
    PlayerFinder(bot)
