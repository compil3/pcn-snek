import logging
import re
import aiohttp

from beanie import Document
from naff import (CommandTypes, Embed, Extension, InteractionContext, Member,
                  OptionTypes, Permissions, check, context_menu, slash_command,
                  slash_option)
from naff.ext.paginators import Paginator
from utils.permissions import user_has_player_role
from utils.player_builder import PlayerBuilder
import json
import utils.log as log_utils


class UserRegistration(Document):
    user_id: int
    discord_full_name: str
    registered_gamer_tag: str
    pcn_url: str
    registered_date: str

    class Collection:
        name = "discord_registered"


logger: log_utils.BotLogger = logging.getLogger(__name__)


class PlayerStats(Extension):

    # @check(user_has_player_role())
    @slash_command(
        "stats",
        description="Look up PCN Stats for yourself or someone else.",
        scopes=[689119429375819951, 442081251441115136],
        default_member_permissions=Permissions.USE_APPLICATION_COMMANDS,
    )
    @slash_option(
        "gamertag", "(Optional) Enter a Gamertag", OptionTypes.STRING, required=False
    )
    async def player_stats(self, ctx: InteractionContext, gamertag: str = None):
        """
        Look up PCN Stats for yourself or someone else.
        """
        await ctx.defer(ephemeral=True)

        if gamertag is None:
            gamertag = ctx.author.display_name
            try:
                display = await PlayerBuilder.builder(self, gamertag)
                # self.builder(gamertag)
                if len(display) != 0:
                    try:
                        paginator = Paginator.create_from_embeds(self.bot, display)
                        # await Paginator(self.bot, ctx, embeds, use_select=False).run()
                        logger.command(ctx, f"{gamertag} found")
                        paginator.show_callback_button = False
                        await paginator.send(ctx)
                    except Exception as e:  # now try it
                        logger.command(ctx, f"Exception in /stats {e}")
                        await ctx.send(embeds=display)  # try this, does it send properly?
                else:
                    logger.command(ctx, f"No player found for {gamertag}")
                    await ctx.send("Unable to retreive your stats.  If you discord name does not match your gamertag, you will need to use /stats [gamertag] or no stats could be found.")
                    return
            except Exception as e:
                raise e  # try this??????
        elif gamertag is not None:
            try:
                display = await PlayerBuilder.builder(self, gamertag)
                if len(display) != 0:
                    try:
                        paginator = Paginator.create_from_embeds(self.bot, *display, timeout=30)
                        paginator.show_callback_button = False
                        logger.command(ctx, f"{gamertag} found, sending paginator")
                        await paginator.send(ctx)
                    except Exception:
                        await ctx.send(ctx)
                else:
                    logger.command(ctx, f"No player found for {gamertag} or no stats found.")
                    await ctx.send(
                        f"Unable to retreive stats for `{gamertag}`. Stats may not exist, please verify on the website if they have any stats added."
                    )
                    return
            except Exception as e:
                logger.command(ctx, f"Exception in /stats {e}")

    # TODO Complete the player stats context menu
    @check(user_has_player_role())
    @context_menu(
        "Stats",
        CommandTypes.USER,
        scopes=[689119429375819951],
        default_member_permissions=Permissions.USE_APPLICATION_COMMANDS,

    )
    async def stats_context(self, ctx: InteractionContext):
        """
        Look up PCN Stats for selected user
        """
        await ctx.defer(ephemeral=True)
        # member = await self.bot.get_member(ctx.target_id, ctx.guild_id)

        post = []
        try:
            member: Member = ctx.target
            registered_user = await UserRegistration.find_one(UserRegistration.user_id == member.id)
            if registered_user is not None:
                post = self.builder(member.display_name)
                if post is not None:
                    paging = Paginator.create_from_embeds(self.bot, *post)
                    paging.show_select_menu = False
                    await paging.send(ctx)
                else:
                    await ctx.send(
                        f"Unable to retreive stats for {member.display_name} stats.  If you know the players gamertag, you will need "
                        "to use /stats [gamertag]."
                    )
                    return
            else:
                await ctx.send(f"`Command unavailable.\n\n{member.display_name}` has not registered with the bot yet.\nIf you know their gamertag, try using `/stats <gamertag>`, and get them to register using `/register <gamertag>`.")
                return
        except Exception as e:
            logging.ERROR(e)

    # TODO create a function to get the player stats, make this async so it can be used on different threads
    async def builder(self, gamertag):
        id = ["21", "27", "26"] # 21 = Super, 27 = League 1, 26 = League 2
        embeds = []
        try:
            if " " in gamertag:
                gamertag = gamertag.replace(" ", "-")

            async with aiohttp.ClientSession() as session:
                async with session.get(self.bot.config.urls.players.format(gamertag)) as response:
                    player_text = await response.text()
                    player_data = json.loads(player_text)
                # url = self.bot.config.urls.players.format(gamertag)
                # player_page = requests.get(url)
                    if len(player_data) < 1:
                        embeds = None
                        return embeds
                    else:
                        player_record = player_data[0]["statistics"]
                        for key in id:
                            index = key
                            for field in player_record[index]:
                                if field != "0":
                                    league_name = None
                                    if index == "21":
                                        league_name = "Super League"
                                    elif index == "27":
                                        league_name = "League One"
                                    elif index == "26":
                                        league_name = "League Two"
                                    if (field == "-1" and "appearances" not in player_record[index][field]):
                                        continue
                                    if (player_record[index][field]["appearances"] == "0"):
                                        continue
                                    if "&#8211;" in player_data[0]["title"]["rendered"]:
                                        player_name = player_data[0]["title"]["rendered"]
                                        playername, status = player_name.split("&#8211;")
                                    else:
                                        playername = player_data[0]["title"]["rendered"]

                                    win_record = str(int(int(player_record[index][field]["appearances"]) * float(player_record[index][field]["winratio"]) / 100))
                                    draw_record = str(
                                        int(int(player_record[index][field]["appearances"]) * float(player_record[index][field]["drawratio"]) / 100))
                                    loss_record = str(int(int(player_record[index][field]["appearances"]) * float(player_record[index][field]["lossratio"]) / 100))
                                    windrawlost = (win_record + "-" + draw_record + "-" + loss_record)
                                    ratio = (
                                        str(player_record[index][field]["winratio"]) + "% - " + str(player_record[index][field]["drawratio"]) + "% - " + str(player_record[index][field]["lossratio"]) + "%")

                                    # Check if the data exists or not.
                                    if (int(player_record[index][field]["appearances"]) < 1 and int(player_record[index][field]["shotsfaced"]) <= 0):
                                        continue

                                    # goalie stats & calculations
                                    elif (int(player_record[index][field]["shotsfaced"]) > 0 and float(player_record[index][field]["saveperc"]) > 0.0):
                                        saveperc = (float(player_record[index][field]["saveperc"]) * 100)
                                        ga = float(player_record[index][field]["goalsagainst"])
                                        mins = (float(player_record[index][field]["appearances"]) * 90)
                                        gaa = float(ga / mins) * 90

                                        if player_record[index][field]["name"] == "Total":
                                            embed = Embed(
                                                title=f"**{league_name} - Career Totals**",
                                                color=0x1815C6,
                                            )
                                            embed.set_author(
                                                name=f"{playername}",
                                                url=f"{player_data[0]['link']}stats",
                                            )
                                            if (
                                                "&#8211;"
                                                in player_data[0]["title"]["rendered"]
                                            ):
                                                embed.set_footer(text=f"Status: {status}")
                                            pass
                                        else:
                                            team_name_clean = re.compile("<.*?>")
                                            team = re.sub(
                                                team_name_clean,
                                                "",
                                                player_record[index][field]["team"],
                                            )
                                            team_link = re.search(
                                                r'href=[\'"]?([^\'" >]+)',
                                                player_record[index][field]["team"],
                                            )
                                            team_link_cleaned = team_link.group(0).replace('href="', "")
                                            embed = Embed(
                                                title=f"**{team}** - {player_record[index][field]['name']}",
                                                url=team_link_cleaned,
                                                color=0x1815C6,
                                            )
                                            embed.set_author(
                                                name=f"{playername} - {league_name}",
                                                url=f"{player_data[0]['link']}stats",
                                            )
                                            if (
                                                "&#8211;"
                                                in player_data[0]["title"]["rendered"]
                                            ):
                                                embed.set_footer(text=f"Status: {status}")
                                        # embed.add_field(name="\u200B", value="```Record```", inline=False)
                                        embed.add_field(
                                            name="Appearances",
                                            value=player_record[index][field]["appearances"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="W-D-L", value=windrawlost, inline=True
                                        )
                                        embed.add_field(
                                            name="Win - Draw - Loss %", value=ratio, inline=True
                                        )
                                        embed.add_field(
                                            name="\u200b", value="```Stats```", inline=False
                                        )
                                        embed.add_field(
                                            name="Save %", value=saveperc, inline=True
                                        )
                                        embed.add_field(
                                            name="Shots Faced",
                                            value=player_record[index][field]["shotsfaced"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Saves",
                                            value=player_record[index][field]["saves"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="GA",
                                            value=player_record[index][field]["goalsagainst"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="GAA", value=round(gaa, 2), inline=True
                                        )
                                        embed.add_field(
                                            name="CS",
                                            value=player_record[index][field]["cleansheets"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="\u200b", value="```Other```", inline=False
                                        )
                                        embed.add_field(
                                            name="Passes Completed",
                                            value=player_record[index][field][
                                                "passescompleted"
                                            ],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Pass Attempts",
                                            value=player_record[index][field][
                                                "passingattempts"
                                            ],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Pass %",
                                            value=f"{player_record[index][field]['passpercent']}%",
                                            inline=True,
                                        )
                                        embeds.append(embed)
                                    # check if player isn't a goalie
                                    elif (int(player_record[index][field]["appearances"]) > 0 and float(player_record[index][field]["saveperc"]) == 0.00):
                                        # player stats and calculations
                                        avgPassPerGame = str(
                                            round(
                                                float(player_record[index][field]["passescompleted"]) / float(player_record[index][field]["appearances"]), 2)
                                        )
                                        tacklesPerGame = str(
                                            round(
                                                float(player_record[index][field]["tackles"]) / float(player_record[index][field]["appearances"]), 2)
                                        )
                                        interceptionsPerGame = str(
                                            round(
                                                float(player_record[index][field]["interceptions"]) / float(player_record[index][field]["appearances"]), 2)
                                        )
                                        tckIntPerGame = (str(tacklesPerGame) + " - " + str(interceptionsPerGame))
                                        possW = str(
                                            round(
                                                float(
                                                    player_record[index][field][
                                                        "possessionswon"
                                                    ]
                                                )
                                            )
                                        )
                                        possL = str(
                                            player_record[index][field]["possessionslost"]
                                        )
                                        possession = possW + " - " + possL
                                        if int(player_record[index][field]["goals"]) > 0:
                                            shotsPerGoal = (
                                                str(
                                                    round(float(player_record[index][field]["shots"]) / float(player_record[index][field]["goals"]), 2,))
                                                + " - "
                                                + str(player_record[index][field]["shpercent"])
                                                + "%"
                                            )
                                        else:
                                            shotsPerGoal = (
                                                "0.0"
                                                + " - "
                                                + str(player_record[index][field]["shpercent"])
                                                + "%"
                                            )
                                        if player_record[index][field]["name"] == "Total":
                                            embed = Embed(
                                                title=f"**{league_name} - Career Totals**",
                                                color=0x1815C6,
                                            )
                                            embed.set_author(
                                                name=f"{playername} - {league_name}",
                                                url=f"{player_data[0]['link']}stats",
                                            )
                                            if (
                                                "&#8211;"
                                                in player_data[0]["title"]["rendered"]
                                            ):
                                                embed.set_footer(text=f"Status: {status}")
                                            pass
                                        else:
                                            team_name_clean = re.compile("<.*?>")
                                            team = re.sub(
                                                team_name_clean,
                                                "",
                                                player_record[index][field]["team"],
                                            )
                                            team_link = re.search(
                                                r'href=[\'"]?([^\'" >]+)',
                                                player_record[index][field]["team"],
                                            )
                                            team_link_cleaned = team_link.group(0).replace(
                                                'href="', ""
                                            )
                                            embed = Embed(
                                                title=f"**{team} - {player_record[index][field]['name']}**",
                                                url=team_link_cleaned,
                                                color=0x1815C6,
                                            )
                                            embed.set_author(
                                                name=f"{playername} - {league_name}",
                                                url=f"{player_data[0]['link']}stats",
                                            )
                                            if (
                                                "&#8211;"
                                                in player_data[0]["title"]["rendered"]
                                            ):
                                                embed.set_footer(text=f"Status: {status}")

                                        # embed.add_field(name="\u200B", value="```Record```", inline=False)
                                        embed.add_field(
                                            name="Appearances",
                                            value=player_record[index][field]["appearances"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="W-D-L", value=windrawlost, inline=True
                                        )
                                        embed.add_field(
                                            name="Win - Draw - Loss %", value=ratio, inline=True
                                        )
                                        embed.add_field(
                                            name="\u200b",
                                            value="```Offensive Stats```",
                                            inline=False,
                                        )
                                        embed.add_field(
                                            name="Goals",
                                            value=player_record[index][field]["goals"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="G/Game",
                                            value=player_record[index][field]["gpg"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="SOG - Shots",
                                            value=str(player_record[index][field]["sog"])
                                            + " - "
                                            + str(player_record[index][field]["shots"]),
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="S/Game",
                                            value=(
                                                str(
                                                    round(
                                                        float(
                                                            player_record[index][field]["shots"]
                                                        )
                                                        / float(
                                                            player_record[index][field][
                                                                "appearances"
                                                            ]
                                                        ),
                                                        2,
                                                    )
                                                )
                                            ),
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Shots/Goal - SH%",
                                            value=shotsPerGoal,
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Assists",
                                            value=player_record[index][field]["assists"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Passes - Pass Attempts",
                                            value=(
                                                str(
                                                    player_record[index][field][
                                                        "passescompleted"
                                                    ]
                                                )
                                                + " - "
                                                + str(
                                                    player_record[index][field][
                                                        "passingattempts"
                                                    ]
                                                )
                                            ),
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Key Passes",
                                            value=player_record[index][field]["keypasses"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Assists/Game",
                                            value=player_record[index][field]["apg"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="P/Game - Pass %",
                                            value=(
                                                str(avgPassPerGame)
                                                + " - "
                                                + str(
                                                    player_record[index][field]["passpercent"]
                                                )
                                                + "%"
                                            ),
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="\u200b",
                                            value="```Defensive and Red Card Stats```",
                                            inline=False,
                                        )
                                        embed.add_field(
                                            name="Tackles",
                                            value=str(player_record[index][field]["tackles"]),
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Interceptions",
                                            value=player_record[index][field]["interceptions"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="TKL-Int/Game",
                                            value=tckIntPerGame,
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="PossW - PossL", value=possession, inline=True
                                        )
                                        embed.add_field(
                                            name="Blocks",
                                            value=player_record[index][field]["blocks"],
                                        )
                                        embed.add_field(
                                            name="Headers Won",
                                            value=player_record[index][field]["headerswon"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Clearances",
                                            value=player_record[index][field]["clearances"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Cleansheets",
                                            value=player_record[index][field]["cleansheets"],
                                            inline=True,
                                        )
                                        embed.add_field(
                                            name="Red Cards",
                                            value=player_record[index][field]["redcards"],
                                            inline=True,
                                        )
                                        embeds.append(embed)
        except Exception as e:
            print(e)
        return embeds


def setup(bot):
    PlayerStats(bot)
    bot.add_model(UserRegistration)
