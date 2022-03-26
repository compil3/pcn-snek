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
    # @Task.create(TimeTrigger(minute=1))
    # async def table_update():
    #     """
    #     Outputs the current table automatically based on a set time frame
    #     """
    #     pass
    @slash_command(
        "table",
        "Display PCN League Tables",
        scopes=[689119429375819951, 442081251441115136],
        default_permission=True,
        # permissions =[
        #     # Permission(910676210172977213, 174342051318464512, PermissionTypes.ROLE, True),  # Player, TheNine
        #     Permission(442081251441115136, 449043802829750272,  PermissionTypes.ROLE, True),
        #   ]  # Player, PCN Discord
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
        await ctx.send("PCN Tables", components=components)

    def get_leagues(self,session):
        tasks = []
        for league in competitions:
            uri = self.config.urls.teams + "?slug=" + league
            tasks.append(session.get(self.config.urls.tables + "?slug=" +league, ssl=False))
            # tasks.append(session.get(configFile['urls']['teams'].format("?slug=" + league), ssl=False))
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
                leagueTable = []
                teamPoints = []
                test_table = dict()
                data = dict()
                test_league = []
                leagueName, season = index[0]['title']['rendered'].split("&#8211;")
                e = Embed(f"**{season}**", color=MaterialColors.GREEN)
                for tablePosition in index[0]['data']:
                    if tablePosition != '0':
                        test_table = {
                            "rank":  str(index[0]['data'][tablePosition ]['pos']),
                            "team":  str(index[0]['data'][tablePosition ]['name']),
                            "points": str(index[0]['data'][tablePosition ]['pts']),
                        }
                        # ranking = str(index[0]['data'][tablePosition ]['pos'])
                        # name = str(index[0]['data'][tablePosition]['name'])
                        # points = str(index[0]['data'][tablePosition]['pts'])
                        # # data = [dict(zip(ranking, (a,b))) for a,b in zip(name, pts)]
                        # test_table[ranking] = name, points
                    test_league.append(test_table)
                        # leagueTable.append(". " + str(index[0]['data'][tablePosition]['name']) + "        | " + str(index[0]['data'][tablePosition]['pts']) + '\n'
                        # )
                        # teamPoints.append(
                        #     str(index[0]['data'][tablePosition]['pts']) + '\n'
                        # )
                
                # teamRanking = " ".join(teamPosition)
                # teamPoints = " ".join(teamPoints)
                e.description= f"```prolog\n{tablemaker.league_tables(test_league)}\n```"
                # e.set_author(f"{leagueName}", url=index[0]['link'])
                # e.add_field("Rank - Pts", leagueTable, inline=True)
                embeds.append(e)
        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        paginator.show_callback_button = False
        await paginator.send(ctx)

    @component_callback("super_league")
    async def super_league_table(self, ctx: ComponentContext):
        pass

    @component_callback("league_one")
    async def league_one_table(self, ctx: ComponentContext):
        pass

    @component_callback("league_two")
    async def league_two_table(self, ctx: ComponentContext):
        pass


    @component_callback("TablePicker")
    async def get_tables(self, ctx:InteractionContext):
        embeds = []
        league_table= []

        match ctx.data['data']['values'][0]:
            case "all":
                async with aiohttp.ClientSession() as session:
                    tasks = self.get_leagues(session)
                    tables = await asyncio.gather(*tasks)

                    for standings in tables:
                        league_table.append(await standings.json())
                    for index in league_table:
                        leagueTable = []
                        teamPoints = []

                        leagueName, season = index[0]['title']['rendered'].split("&#8211;")
                        e = Embed(f"**{season}**", color=MaterialColors.GREEN)
                        for tablePosition in index[0]['data']:
                            if tablePosition != '0':
                                leagueTable.append(
                                    + ". "
                                    + str(index[0]['data'][tablePosition]['name'])
                                    + "        | "
                                    + str(index[0]['data'][tablePosition]['pts'])
                                    + '\n'
                                )
                                teamPoints.append(
                                    str(index[0]['data'][tablePosition]['pts']) + '\n'
                                )
                        # teamRanking = " ".join(teamPosition)
                        teamPoints = " ".join(teamPoints)
                        e.set_author(f"{leagueName}", url=index[0]['link'])
                        e.add_field("Rank - Pts", leagueTable, inline=True)
                        embeds.append(e)
                return embeds
            case "super-league":
                page =  Paginator(ctx.message.channel, ctx.message.author, "", embeds)




def setup(bot):
    Tables(bot)