import asyncio
import logging
import time


from aiohttp_client_cache import CachedSession, SQLiteBackend
from helpers import tablemaker

from naff.ext.paginators import Paginator
from naff.models import Embed, Extension
from naff.models.discord.color import MaterialColors
from naff.models.discord.components import ActionRow, Button, ButtonStyles
from naff.models.naff.application_commands import (Permissions,
                                                   component_callback,
                                                   slash_command)
from naff.models.naff.context import ComponentContext
from utils.permissions import user_has_player_role


urls_expire_after ={
    "proclubsnation.com": 300,
}
cache = SQLiteBackend (
    cache_name='cache.db',
    expires_after=300,
    urls_expire_after=urls_expire_after,
    timeout=5
)

class Tables(Extension):

    # @check(user_has_player_role())
    @slash_command(
        "table",
        description="Display PCN League Tables",
        scopes=[689119429375819951, 442081251441115136],
        default_member_permissions=Permissions.USE_APPLICATION_COMMANDS
    )

    async def create_table(self, ctx: ComponentContext):
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

    def get_league_tables(self,session):
        tasks = []
        competitions = ["super-league", "league-one", "league-two"]
        for league in competitions:
            tasks.append(session.get(self.bot.config.urls.tables.format(league), ssl=False))
        return tasks

    @component_callback("all_leagues")
    async def pcn_table(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        embeds = []
        league_table= []
        start_time = time.time()
        async with CachedSession(cache=cache) as session:
            tasks = self.get_league_tables(session)
            tables = await asyncio.gather(*tasks)
            end_time = time.time() - start_time
            for standings in tables:
                league_table.append(await standings.json())
            for index in league_table:
                table = dict()
                league_table = []

                leagueName, season = index[0]['title']['rendered'].split("&#8211;")
                e = Embed(f"**PCN {leagueName}Table**\n{season}", color=MaterialColors.RED)
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
                e.description = f"```prolog\n{tablemaker.league_tables(league_table)}\n```"
                # e.add_field("Time", end_time, inline=False)
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
        async with CachedSession(cache=cache) as session:
            async with session.get(self.bot.config.urls.tables.format(league), ssl=False) as resp:
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
