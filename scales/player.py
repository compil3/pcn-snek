import logging
from dis_snek.models.application_commands import PermissionTypes
from dis_snek.models.context import InteractionContext
from dis_snek.models.enums import CommandTypes
import requests
import asyncio
import re
import motor.motor_asyncio as moto

from dis_snek.models import (Embed, Scale, Permission, context_menu, slash_command, slash_permission, MaterialColors,
                             slash_option, check)
from snek_paginator import Paginator

from extensions import default

config = default.config()

default_player_url = config['urls']['find_player']

guildid = 689119429375819951
role_id = 843899510483976233

user_perm = [Permission(842505724458172467,PermissionTypes.ROLE, True)]

class PlayerStats(Scale):

    @slash_command(
        "pcn_test",
        # pip install --U --force git+https://github.com/Discord-Snake-Pit/Dis-Snek.git  I use poetry just downlaod the git version not pypi wonder if that it
        #  dis-snek = {git = "https://github.com/Discord-Snake-Pit/Dis-Snek.git"}  is what poetry uses  Wonder if I have to change all the command permissions because of v2
        #  actually find.py uses the new permissions and it's greyed out.  So i don't know what's going on. discord could just be fkn wack i t  woTrked for me so i have no clue
        #   I'm going to make a new command and copy pasta your test command  see if it works :|, maybe because i have delete_unused on it's fucking up
        
        # bot = Snake(
        #     sync_interactions=True,
        #     delete_unused_application_cmds=True,
        #     default_prefix="⭐",
        #     activity="with the stars 🌠",
        # ) this is mine
        #  I honestly have no idea.  Switch to test.py
        

        "Look up PCN Stats for yourself or someone else.", 
        scopes=[689119429375819951],
        default_permission=False, 
        # Player Role, Guildid
        permissions=[
            Permission(843899510483976233, 689119429375819951, PermissionTypes.ROLE, True)
        ],
    )
    # @slash_permission(
    #     guild_id=guildid, 
    #     permissions=[
    #         Permission(111252573054312448,PermissionTypes.USER, True),
    #         Permission(843899510483976233, PermissionTypes.ROLE, True),
    #     ],
    # )
    @slash_option("gamertag", "(Optional) Enter a Gamertag", 3, required=False)
    async def player_stats(self, ctx: InteractionContext, gamertag: str):
        """
        Look up PCN Stats for yourself or someone else.
        """
        await ctx.defer(ephemeral=True)
        post = []
        if gamertag is None:
            gamertag = ctx.author.display_name
            try:
                post = self.builder(gamertag, False)
                if post is not None:
                    await Paginator(self.bot, ctx, post).run()
                else:
                    await ctx.send(
                        "Unable to retreive your stats.  If you discord name does not match your gamertag, you will need to use /stats [gamertag].")
                    return
            except Exception as e:
                logging.ERROR(e)
        elif gamertag is not None:
            try:
                post = self.D_Embed(gamertag, True)
                if post is None:
                    await ctx.send(f"Unable to retreive stats for {gamertag}.  Please check the tag and try again.")
                    return
                else:
                    ...
            except Exception as e:
                logging.ERROR(e)

    # TODO Complete the player stats context menu
    @context_menu("Stats", context_type=CommandTypes.USER, scopes=[guildid], default_permission=False,
                  permissions=user_perm)
    async def stats_context(self, ctx: InteractionContext):
        """
        Look up PCN Stats for selected user
        """
        await ctx.defer(ephemeral=True)
        member = await self.bot.get_member(ctx.target_id, ctx.guild_id)
        url = default_player_url.format(member.display_name)
        post = []
        gamertag = ctx.author.display_name
        try:
            post = self.builder(gamertag, False)
            if post is not None:
                # TODO add paginator here
                ...
            else:
                await ctx.send(
                    "Unable to retreive your stats.  If you discord name does not match your gamertag, you will need "
                    "to use /stats [gamertag].")
                return
        except Exception as e:
            logging.ERROR(e)
            
    # TODO create a function to get the player stats
    async def builder(self, gamertag, param):
        uuid = ["21", "26", "27"]
        embeds = []
        url = default_player_url.format(gamertag)

        # # Use this to pull filtered player and stats at the same time (faster)
        # #  async def get_async(url):
        # async with httpx.AsyncClient(timeout=None) as client:
        #     return await client.get(url)

        # resps = await asyncio.gather(*map(self.playerapi, urls))


        try:
            # TODO async request to full profile and filtered version
            page = requests.get(url)

            if page.status_code == 200:
                if page.json()[0] is None:
                    raise IndexError
                else:
                    record = page.json()[0]['statistics']
                    for key in uuid:
                        index = key
                        for field in record[index]:
                            if field != "0":
                                league_name = None
                                match index:
                                    case "21":
                                        league_name = "Super League"
                                    case "27":
                                        league_name= "League One"
                                    case "26":
                                        league_name = "League Two"
                                if field == "-1" and "appearances" not in record[index][field] :
                                    continue

                                if "&#8211;" in record.json()[0]["title"]["rendered"]:
                                    player_name = record.json()[0]["title"]["rendered"]
                                    playername, status = player_name.split("&#8211;")
                                else:
                                    playername = record.json()[0]['title']['rendered']

                                win_record = str(int(record[index][field]["appearances"]) * float(record[index][field]["winratio"]) / 100)
                                draw_record = str(int(record[index][field]["appearances"])* float(record[index][field]["drawratio"]) / 100)
                                loss_record = str(int(record[index][field]["appearances"])* float(record[index][field]["lossratio"]) /100)
                                windrawlost = win_record + "-" + draw_record + "-"+ loss_record
                                ratio = (
                                    str(record[index][field]["winratio"])
                                    + "% - "
                                    +str(record[index][field]["drawratio"])
                                    + "% - "
                                    + str(record[index][field]["lossratio"])
                                    + "%"
                                )

                                # Check if the data esists or not
                                if int(record[index][field]["appearances"]) < 1 and float(record[index][field]["shotsfaced"]) <= 0:
                                    continue
                                # goalie stats & calculations
                                elif int(record[index][field]["shotsfaced"]) > 0 and float(record[index][field]["saveperc"]) > 0.0:
                                    saveperc = float(record[index][field]["saveperc"]) * 100
                                    ga = float(record[index][field]["goalsagainst"])
                                    mins = float(record[index][field]["appearances"]) * 90
                                    gaa = float(ga/mins) * 90

                                    if record[index][field]["name"] == "Total":
                                        e = Embed(f"**{league_name} - Career Totals**", color=MaterialColors.BLUE_GREY)
                                        e.set_author(f"{playername}", url=f"{record.json()[0]['link']}")

                                        if "&#8211;" in record.json()[0]["title"]["rendered"]:
                                            e.set_footer(f"Status: {status}")
                                            pass
                                    else:
                                        team = re.sub(r'<.*?>', '', record[index][field]["team"])
                                        team_link = re.search(
                                            r'href=[\'"]?([^\'" >]+)',
                                            record[index][field]["team"],
                                        )
                                        team_link = team_link.group(0).replace('href="',"")

                                        e = Embed(f"**{team}** - {record[index][field]['name']}**", url=team_link, color=MaterialColors.BLUE_GREY)
                                        e.set_author(f"{player_name} - {league_name}", ur=f"{record.json()[0]['link']} stats")

                                        if  "&#8211;" in record.json()[0]['title']['rendered']:
                                            e.set_footer(f"Status: {status}")
                                            pass
                                    e.add_field(name="\u200B", value="```Record```", inline=False)
                                    e.add_field("Appearances", record[index][field]["appearances"], inline=True)
                                    e.add_field("W-D-L", windrawlost, inline=True)
                                    e.add_field("Win - Draw - Loss %", ratio, inline=True)
                                    e.add_field("\u200b", value="```Stats```", inline=False)
                                    e.add_field("Save %", saveperc, inline=True)
                                    e.add_field("Shots Faced", record[index][field]["shotsfaced"], inline=True)
                                    e.add_field("Saves", record[index][field]["saves"], inline=True)
                                    e.add_field("Goals Against", record[index][field]["goalsagainst"], inline=True)
                                    e.add_field("Goals Against Average", round(gaa,2),  inline=True)
                                    e.add_field("CS", record[index][field]["cleansheets"], inline=True)
                                    e.add_field("\u200b", "```Other```", inline=False)
                                    e.add_field("Passes Completed", record[index][field]["passedcompleted"], inline=True)
                                    e.add_field("Passes Attempted", record[index][field]["passedattempted"], inline=True)
                                    e.add_field("Pass %", f"{record[index][field]['passperc']} %", inline=True)
                                    embeds.append(e)
                                
                                elif int(record[index][field]["appearances"]) > 0 and float(record[index][field]['saveperc']) == 0.00:
                                    avgPassPerGame = str(round(float(record[index][field]['passescompleted']) / float(record[index][field]['appearances']),2))
                                    tacklesPerGame = str(round(float(record[index][field]['tackles']) / float(record[index][field]['appearances']),2))
                                    interceptionsPerGame = str(round(float(record[index][field]['interceptions']) / float(record[index][field]['appearances']),2))
                                    tckIntPerGame = str(tacklesPerGame + " - " + str(interceptionsPerGame))

                                    possW = str(record[index][field]['possessionwon'])
                                    possL = str(record[index][field]['possessionlost'])
                                    possession = possW + " - " + possL

                                    if int(record[index][field]['goals']) > 0:
                                        shotsPerGoal = str(round(float(record[index][field]['shots']) / float(record[index][field]['goals']),2)) + " - " + str(record[index][field]['shpercent'] + "%")
                                    else:
                                        shotsPerGoal = "0.0" + " - " + str(record[index][field]['shpercent'] + "%")
                                    
                                    if record[index][field]['name'] == "Total":
                                        e = Embed(f"**{league_name} - Career Totals**", color=MaterialColors.BLUE_GREY)
                                        e.set_author(f"{playername}", url=f"{record.json()[0]['link']} stats")

                                        if  "&#8211;" in record.json()[0]['title']['rendered']:
                                            e.set_footer(f"Status: {status}")
                                        pass

                                    else:
                                        team = re.sub(r'<.*?>', '', record[index][field]["team"])
                                        team_link = re.search(
                                            r'href=[\'"]?([^\'" >]+)',
                                            record[index][field]["team"],
                                        )
                                        team_link = team_link.group(0).replace('href="',"")
                                        e.Embed(f"**{team}** - {record[index][field]['name']}**", url=team_link, color=MaterialColors.BLUE_GREY)
                                        e.set_author(f"{player_name} - {league_name}", ur=f"{record.json()[0]['link']} stats")
                                        if "&#8211;" in page.json()[0]["title"]["rendered"]:
                                            e.set_footer(f"Status: {status}")
                                        
                                        e.add_field(name="\u200B", value="```Record```", inline=False)
                                        e.add_field("Appearances", record[index][field]["appearances"], inline=True)
                                        e.add_field("W-D-L", windrawlost, inline=True)
                                        e.add_field("Win - Draw - Loss %", ratio, inline=True)
                                        e.add_field("\u200b", value="```Offensive Stats```", inline=False)
                                        e.add_field("Goals", record[index][field]["goals"], inline=True)
                                        e.add_field("G/Game", record[index][field]['gpg'], inline=True)
                                        e.add_field("SOG - Shots", str(record[index][field]['sog']) + " - " + str(record[index][field]['shots']), inline=True)
                                        e.add_field("Sh/Game", str(round(float(record[index][field]['shots']) / float(record[index][field]['appearances']),2)), inline=True)
                                        e.add_field("Shots/Goal - SH %", shotsPerGoal, inline=True)
                                        e.add_field("Assists", record[index][field]["assists"], inline=True)
                                        e.add_field("Passes - Pass Attempts", record[index][field]["passescompleted"] + " - " + record[index][field]["passesattempted"], inline=True)
                                        e.add_field("Key Passes", record[index][field]['keypasses'], inline=True)
                                        e.add_field("Assists/Game", record[index][field]['apg'], inline=True)
                                        e.add_field("P/Game - Pass %", str(avgPassPerGame) + " - " + str(record[index][field]['passpercent'] + "%"), inline=True)
                                        e.add_field("\u200b", value="```Defensive And Red Card Stats```", inline=False)
                                        e.add_field("Tackles", str(record[index][field]['tackles']), inline=True)
                                        e.add_field("Interceptions", record[index][field]['interceptions'], inline=True)
                                        e.add_field("TKL-Int/Game", tckIntPerGame, inline=True)
                                        e.add_field("PossW - PossL", possession, inline=True)
                                        e.add_field("Blocks", record[index][field]['blocks'], inline=True)
                                        e.add_field("Headers Won", record[index][field]['headerswon'], inline=True)
                                        e.add_field("Clearances", record[index][field]['clearances'], inline=True)
                                        e.add_field("Cleansheets", record[index][field]['cleansheets'], inline=True)
                                        e.add_field("Red Cards", record[index][field]['redcards'], inline=True)
                                        embeds.append(e)
        except Exception as e:
            print(e)
        return embeds

def setup(bot):
    PlayerStats(bot)



                            






