import logging
import re
import aiohttp
import functools
from beanie import Document
from naff import (CommandTypes, Embed, Extension, InteractionContext, Member,
                  OptionTypes, Permissions, check, context_menu, slash_command,
                  slash_option)
from naff.ext.paginators import Paginator
from utils.permissions import user_has_player_role
from utils.player_builder import PlayerBuilder
import json
import utils.log as log_utils
from functools import cache
from loguru import logger


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
                        logger.error(ctx, f"{gamertag} found")
                        paginator.show_callback_button = False
                        await paginator.send(ctx)
                    except Exception as e:  # now try it
                        logger.error(ctx, f"Exception in /stats {e}")
                        await ctx.send(embeds=display)  # try this, does it send properly?
                else:
                    logger.error(ctx, f"No player found for {gamertag}")
                    await ctx.send("Unable to retreive your stats.  If you discord name does not match your gamertag, you will need to use /stats [gamertag] or no stats could be found.")
                    return
            except Exception as e:
                raise e  # try this??????
        elif gamertag is not None:
            try:
                display = await PlayerBuilder.builder(self, gamertag)
                if len(display) != 0:
                    try:
                        paginator = Paginator.create_from_embeds(self.bot, *display)
                        paginator.show_callback_button = False
                        logger.info(ctx, f"{gamertag} found, sending paginator")
                        await paginator.send(ctx)
                    except Exception:
                        await ctx.send(ctx)
                else:
                    logger.info(ctx, f"No player found for {gamertag} or no stats found.")
                    await ctx.send(
                        f"Unable to retreive stats for `{gamertag}`. Stats may not exist, please verify on the website if they have any stats added."
                    )
                    return
            except Exception as e:
                logger.error(ctx, f"Exception in /stats {e}")

    # TODO Complete the player stats context menu
    # @check(user_has_player_role())
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
                post = await PlayerBuilder.builder(self,registered_user.registered_gamer_tag)
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

def setup(bot):
    PlayerStats(bot)
    bot.add_model(UserRegistration)
