import logging
import re
import requests
import aiohttp
import motor.motor_asyncio as motor

from dis_snek.models import (
    Scale,
    Embed,
    Permission,
    command,
    slash_command,
    slash_option,
    slash_permission,
    check
)

from datetime import datetime
from dotenv import load_dotenv
from os import environ

from extensions import default


load_dotenv()
config = default.config()
default_player_url = config['urls']['players']

guild_ids=689119429375819951
admin_perm = [Permission(842505724458172467, 1, True)]
class PlayerFinder(Scale):

    @slash_command(
        "find",
        description="Staff only",
        scope=int(config['guilds']['Nine2']['id']),
        default_permission=False
    )
    @slash_permission(
        guild_id=int(config['guilds']['Nine2']['id']), permissions=admin_perm)
    @slash_option("gamertag", "Enter Gamertag to check", 3, required=True)
    async def find(self, ctx, gamertag: str):
        await ctx.defer(ephemeral=True)
        
        lookup_gt = gamertag
        embed = Embed(title="PCN Player Lookup")
        embed.set_author(
            name="PCN Player Lookup",
            url="https://proclubsnation.com",
            icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
        )
        if bool(re.search(r"\s", gamertag)):
            lookup_gt = gamertag.replace(' ', '-')
        else:
            pass
        
        try:
            url = default_player_url.format(lookup_gt)
            players_page = requests.get(url) 
            try:
               players_page.json()[0]['id'] is None
            except IndexError:
                embed.add_field(name="Gamertag", value=f"``{gamertag}``", inline=False)
                # embed.add_field(name="Discord User", value=..., inline=False)
                embed.add_field(name="Result", value="Gamertag Not Found.", inline=False)
                await ctx.send(embeds=[embed])
            else:
                page = players_page.json()[0]['link']
                embed.add_field(name="Gamertag", value=f"``{gamertag}``", inline=False)
                # embed.add_field(name="Discord User", value=member.mention, inline=True)
                embed.add_field(name="Result", value="Gamertag found.", inline=False)
                embed.add_field(name="Profile", value=players_page.json()[0]['link'], inline=False)
                await ctx.send(embeds=[embed])
  
        except Exception as e:
            print(e)

    # @slash_command(
    #     "find",
    #     description="Check player Gamertag is vetted on the site.",
    #     scope=config['guilds']['TheNine']['id'],
    # )
    # @slash_permission(guild_id=config['guilds']['TheNine']['id'], permissions=[Permission(config['guilds']['TheNine']['mod'],2,False)])
    # @slash_option("gamertag", "Enter Gamertag to check", 3, required=True)
    # async def findtest(self, ctx, gamertag: str):
    #     await ctx.defer(ephemeral=True)

    #     lookup_gt = gamertag
    #     embed = Embed(title="PCN Player Lookup")
    #     embed.set_author(
    #         name="PCN Player Lookup",
    #         url="https://proclubsnation.com",
    #         icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
    #     )
    #     if bool(re.search(r"\s", gamertag)):
    #         lookup_gt = gamertag.replace(' ', '-')
    #     else:
    #         pass
        
    #     try:
    #         url = default_player_url.format(lookup_gt)
    #         players_page = requests.get(url) 
    #         try:
    #            players_page.json()[0]['id'] is None
    #         except IndexError:
    #             embed.add_field(name="Gamertag", value=f"``{gamertag}``", inline=False)
    #             # embed.add_field(name="Discord User", value=..., inline=False)
    #             embed.add_field(name="Result", value="Gamertag Not Found.", inline=False)
    #             await ctx.send(embeds=[embed])
    #         else:
    #             page = players_page.json()[0]['link']
    #             embed.add_field(name="Gamertag", value=f"``{gamertag}``", inline=False)
    #             # embed.add_field(name="Discord User", value=member.mention, inline=True)
    #             embed.add_field(name="Result", value="Gamertag found.", inline=False)
    #             embed.add_field(name="Profile", value=players_page.json()[0]['link'], inline=False)
    #             await ctx.send(embeds=[embed])
  
    #     except Exception as e:
    #         print(e)


def setup(bot):
    PlayerFinder(bot)