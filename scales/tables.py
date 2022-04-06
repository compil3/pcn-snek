import asyncio
import logging
from tabnanny import check
import aiohttp
from dis_snek.models.snek.application_commands import (
    OptionTypes,
    Permission,
    PermissionTypes,
    SlashCommandChoice,
    SlashCommandOption,
    component_callback,
    slash_command,
    slash_option,
    slash_permission
)
from dis_snek.models.discord.components import ActionRow, Button, ButtonStyles
from dis_snek.models.discord.color import MaterialColors
from dis_snek.models.snek.context import InteractionContext, ComponentContext
from dis_snek.models.snek import Task, TimeTrigger
from dis_snek.models import Embed, Scale
from dis_snek.models.discord.enums import Status
from dis_snek.ext.paginators import Paginator

from extensions import default, tablemaker
from config import load_settings


competitions = ["super-league", "league-one", "league-two"]
configFile = default.get_config()
config = None
class Tables(Scale):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_settings()
        config = self.config

    @slash_command(
        "table",
        "Display PCN League Tables",
        scopes=[689119429375819951, 442081251441115136],
        default_permission=True,
    )
    @slash_permission(
        # Permission(910676210172977213, 174342051318464512, PermissionTypes.ROLE, True),  # Player, TheNine
        Permission(442081251441115136, 449043802829750272,  PermissionTypes.ROLE, True), # Player, PCN Discord      
    )
    async def create_table(self, ctx: ComponentContext): # pylint: disable=R0914
        await ctx.defer(ephemeral=True)
        try:           
            components: list[ActionRow]=[
               Button(
                   style=ButtonStyles.BLURPLE,
                   label="All Leagues",
                   custom_id="all_leagues",
               ),
               Button(
                   style=ButtonStyles.BLURPLE,
                   label="Super League",
                   custom_id="super_league",
               ),
               Button(
                   style=ButtonStyles.BLURPLE,
                   label="League One",
                   custom_id="league_one",
               ),
               Button(
                   style=ButtonStyles.BLURPLE,
                   label="League Two",
                   custom_id="league_two",
               )
           ]
        except Exception as e:
                logging.ERROR(e)
        await ctx.send("PCN Standings", components=components)

    def get_leagues(self,session):
        tasks = []
        for league in competitions:
            tasks.append(session.get(self.config.urls.tables + "?slug=" +league, ssl=False))
        return tasks

    @component_callback("all_leagues")
    async def pcn_table(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        embeds = []
        league_table= []

        async with aiohttp.ClientSession() as session:
            tasks = self.get_leagues(session)
            tables = await asyncio.gather(*tasks)

            for standings in tables:
                league_table.append(await standings.json())
            for index in league_table:
                table = dict()
                league_table = []

                leagueName, season = index[0]['title']['rendered'].split("&#8211;")
                e = Embed(f"**{leagueName}\n{season}**", color=MaterialColors.RED)
                for tablePosition in index[0]['data']:
                    if tablePosition != '0':
                        table = {
                            "rank":  str(index[0]['data'][tablePosition]['pos']),
                            "team":  str(index[0]['data'][tablePosition]['name']),
                            "points": str(index[0]['data'][tablePosition]['pts']),
                        }
                        league_table.append(table)
                    else:
                        pass
                e.description= f"```prolog\n{tablemaker.league_tables(league_table)}\n```"
                embeds.append(e)
        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        paginator.show_callback_button = False
        await paginator.send(ctx)

    @component_callback("super_league")
    async def super_league_table(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        e = await self.get_standings("super-league")
        await ctx.send(embeds=[e], components=[])
        
    @component_callback("league_one")
    async def league_one_table(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        e = await self.get_standings("league-one")
        await ctx.send(embeds=[e], components=[])

    @component_callback("league_two")
    async def league_two_table(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        e = await self.get_standings("league-two")
        await ctx.send(embeds=[e], components=[])


    async def get_standings(self, league: str):
        league_table = []
        async with aiohttp.ClientSession() as session:
            async with session.get(self.config.urls.tables + f"?slug={league}", ssl=False) as resp:
                standing_data = await resp.json()
                league_name, season_number = standing_data[0]['title']['rendered'].split("&#8211;")
                e = Embed(f"**{league_name}\n{season_number}**", color=MaterialColors.RED)

                for tablePosition in standing_data[0]['data']:
                    if tablePosition != '0':
                        table = {
                            "rank":  str(standing_data[0]['data'][tablePosition]['pos']),
                            "team":  str(standing_data[0]['data'][tablePosition]['name']),
                            "points": str(standing_data[0]['data'][tablePosition]['pts']),
                        }
                        league_table.append(table)  
                    else:
                        pass
                e.description= f"```prolog\n{tablemaker.league_tables(league_table)}\n```"
        return e

def setup(bot):
    Tables(bot)