from datetime import datetime
import logging
import requests
from beanie import Document
from naff import (Extension, Embed, slash_command, slash_option, InteractionContext, context_menu, Permissions, CommandTypes)
from naff.models.discord.color import MaterialColors
import utils.log as log_utils

logger: log_utils.BotLogger = logging.getLogger(__name__)

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


class PlayerFinder(Extension):
    # def __init__(self, bot):
    #     self.bot = bot
    #     self.config = load_settings()
    #     # config = self.config

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

    @slash_command(
        "find",
        description="Look up a gamertag",
        scopes=[689119429375819951, 442081251441115136],
        default_member_permissions=Permissions.BAN_MEMBERS | Permissions.MUTE_MEMBERS
    )
    @slash_option("gamertag", "Enter Gamertag to check", 3, required=True)
    async def find(self, ctx: InteractionContext, gamertag: str):
        """Finds a player using /find [gamertag]"""
        # await ctx.send(f"Searching for {gamertag}...", ephemeral=True)
        await ctx.defer(ephemeral=True)
        # try:
        url = self.bot.config.urls.find_player.format(
            f"{gamertag}&_fields=title,link,date,modified,slug"
        )
        try:
            r = requests.get(url)
            if r.status_code == 200:
                if r.json()[0] is None:
                    raise IndexError
                else:
                    e = self.D_Embed(f"**{r.json()[0]['title']['rendered']}**")
                    e.add_field("Registered", r.json()[0]["date"], inline=True)
                    e.add_field("Last Updated", r.json()[0]["modified"], inline=True)
                    e.add_field("Slug", r.json()[0]["slug"])
                    e.add_field("PCN Profile", r.json()[0]["link"])
                    logger.command(ctx, f"Found {gamertag}")
                    await ctx.send(embeds=[e])
            else:
                e = self.D_Embed("Connection Error")
                e.description = "Failed to connect to API.\n\n{e}\n\nTry again later."
                logger.command(ctx, f"Failed to connect to API {r.status_code}")
                await ctx.send(embeds=[e])
        except IndexError:
            e = self.D_Embed("Results")
            e.description = f"**{gamertag}** not found"
            logger.command(ctx, f"{gamertag} not found")
            await ctx.send(embeds=[e])

    # TODO Use the register command to add users to database.  Then pull the gamer tag from the database and use it to find the player.
    @context_menu(
        "Search", CommandTypes.USER, scopes=[689119429375819951, 442081251441115136], default_member_permissions=Permissions.BAN_MEMBERS | Permissions.MUTE_MEMBERS, dm_permission=False
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
            r = requests.get(self.bot.config.urls.find_player.format(f"{find_user.registered_gamer_tag}&_fields=title,link,date,modified,slug"))
            if r.status_code == 200:
                if r.json()[0] is None:
                    raise IndexError
                else:
                    e = self.D_Embed(f"**{r.json()[0]['title']['rendered']}**")
                    e.add_field(
                        "Registered GT", find_user.registered_gamer_tag, inline=False
                    )
                    e.add_field("Discord ID", str(member))
                    e.add_field("Registation Date", r.json()[0]["date"], inline=False)
                    e.add_field("Last Updated", r.json()[0]["modified"], inline=False)
                    e.add_field("API Slug", r.json()[0]["slug"])
                    e.add_field("PCN Profile", r.json()[0]["link"])
                    await ctx.send(embeds=[e])
            else:
                e = self.D_Embed("Connection Error")
                e.description = "Failed to connect to API.\n\n{e}\n\nTry again later."
                await ctx.send(embeds=[e])
        except IndexError:
            e = self.D_Embed("Results")
            e.description = f"**{member}** is not registered with Bot."
            # e.add_field("Registered GT", "Not Registered with Bot", inline=False)
            await ctx.send(embeds=[e])


def setup(bot):
    PlayerFinder(bot)
    bot.add_model(Registered)
