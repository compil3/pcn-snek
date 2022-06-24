import asyncio
import datetime
import logging
import platform
import subprocess
from io import BytesIO
from pathlib import Path

import httpx
import psutil
from aiofile import AIOFile, LineReader
from naff.client.const import __py_version__, __version__
from naff.ext.debug_extension import utils as _d_utils
from naff.models import Embed, Extension, MaterialColors, Timestamp
from naff.models.discord.embed import EmbedField
from naff.models.discord.enums import Intents
from naff.models.discord.file import File
from naff.models.naff.application_commands import Permissions, slash_command
from naff.models.naff.command import cooldown
from naff.models.naff.context import InteractionContext
from naff.models.naff.cooldowns import Buckets
from rich.console import Console
from utils import get_repo_hash

# from naff.ext.debug_ext import utils as _d_utils


def strf_delta(time_delta: datetime.timedelta, show_seconds=True) -> str:
    """Formats timedelta into a human readable format"""

    years, days = divmod(time_delta.days, 365)
    hours, rem = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    years_fmt = f"{years}, year{'s' if years >1 or years == 0 else ''}"
    days_fmt = f"{days} day{'s' if days > 1 or days == 0 else ''}"
    hours_fmt = f"{hours} hour{'s' if hours > 1 or hours == 0 else ''}"
    minutes_fmt = f"{minutes} minute{'s' if minutes > 1 or minutes == 0 else ''}"
    seconds_fmt = f"{seconds} second{'s' if seconds > 1 or seconds == 0 else ''}"

    if years >= 1:
        return f"{years_fmt} and {days_fmt}"
    if days >= 1:
        return f"{days_fmt} and {hours_fmt}"
    if hours >= 1:
        return f"{hours_fmt} and {minutes_fmt}"
    if show_seconds:
        return f"{minutes_fmt} and {seconds_fmt}"
    return f"{minutes_fmt}"


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


class BotInfo (Extension):
    def D_Embed(self, title: str) -> Embed:
        e = Embed(
            f"PCN Bot Debug: {title}",
            color=MaterialColors.BLUE_GREY,
        )
        e.set_footer(
            "PCN Debug Scale",
            icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
        )
        return e

    async def get_async(url):
        async with httpx.AsyncClient(timeout=None) as client:
            return await client.get(url)

    @slash_command(
        "bot",
        sub_cmd_description="Basic information regarding the bot.",
        sub_cmd_name="info",
        scopes=[689119429375819951, 442081251441115136],
        default_member_permissions=Permissions.MANAGE_ROLES | Permissions.KICK_MEMBERS | Permissions.BAN_MEMBERS
    )
    async def debug_info(self, ctx):
        await ctx.defer(ephemeral=True)
        urls = []
        for sites, value in self.bot.config.urls.items():
            match sites:
                case "find_player":
                    value.format("Spillshot")
                case "teams":
                    value = value.replace("/v2/teams", "/v2/teams?slug=ac-milan")
                case "schedules":
                    value = value
            urls.append(value)
        try:
            resps = await asyncio.gather(*map(BotInfo.get_async, urls))
            for data in resps:
                if "teams" in str(data.request.url):
                    team_delay = round(data.elapsed.total_seconds(), 2)
                elif "players" in str(data.request.url):
                    player_delay = round(data.elapsed.total_seconds(), 2)
                elif "tables" in str(data.request.url):
                    table_delay = round(data.elapsed.total_seconds(), 2)
                elif "calendars" in str(data.request.url):  # local variable 'schedule_delay' referenced before assignment
                    schedule_delay = round(data.elapsed.total_seconds(), 2)
        except httpx.ConnectError:
            return await ctx.send("Could not connect to the API. Please try again later.")

        startTime = self.bot.start_time
        print(startTime)
        uptime = datetime.datetime.now() - self.bot.start_time
        e = self.D_Embed("Information")
        e.add_field("Bot Version", f"{self.bot.config.version}", inline=False)
        e.add_field("Language Info", f"NAFF@{__version__}  |  Py@{__py_version__}", inline=True)
        e.add_field("Git Hash", get_repo_hash()[:7], inline=True)
        e.add_field("Start Time", f"{Timestamp.fromdatetime(self.bot.start_time)}\n({strf_delta(uptime)}) ago")
        e.add_field("Operating System", platform.platform(), inline=True)
        e.add_field(name="CPU", value=f"**{psutil.cpu_count(logical=False)} | {psutil.cpu_percent()}%**", inline=True)
        e.add_field(name="RAM", value=f"**{psutil.virtual_memory().percent}**%", inline=True)

        e.add_field("Loaded Extensions", ",".join(self.bot.ext))
        guild_names = []
        for guild in self.bot.guilds:
            guild_names.append(guild.name)
        e.add_field(f"Connected to **{len(self.bot.guilds)}** Guilds", guild_names)
        privileged_intents = [i.name for i in self.bot.intents if i in Intents.PRIVILEGED]
        if privileged_intents:
            e.add_field("Intents", " | ".join(privileged_intents), inline=True)

        e.add_field(name="\u200b", value="**API Status**", inline=False)
        e.add_field(name="Bot", value=f"```{round(self.bot.latency * 100, 2)}s ```", inline=True)
        e.add_field(name="Player API", value=f"```{player_delay}```", inline=True)
        e.add_field(name="\u200b", value="\u200b", inline=True)

        e.add_field(name="Table API", value=f"```{table_delay}```", inline=True)
        e.add_field(name="Teams API", value=f"```{team_delay}```", inline=True)
        e.add_field("Calendar API", f"```{schedule_delay}```", inline=True)
        await ctx.send(embeds=[e])

    @debug_info.subcommand(
        "cache",
        sub_cmd_description="Get information about the cache.",
    )
    async def debug_cache(self, ctx: InteractionContext) -> None:
        await ctx.defer(ephemeral=True)

        e = self.D_Embed("Cache")
        e.description = f"```prolog\n{_d_utils.get_cache_state(self.bot)}\n```"

        await ctx.send(embeds=[e])

    @debug_info.subcommand("lines", sub_cmd_description="Get PCN Bot lines of code")
    @cooldown(bucket=Buckets.CHANNEL, rate=1, interval=30)
    async def _lines(self, ctx: InteractionContext) -> None:
        await ctx.defer(ephemeral=True)
        output = subprocess.check_output(["tokei", "-C", "--sort", "code"]).decode("utf-8")
        await ctx.send(f"```haskell\n{output}\n```")

    @debug_info.subcommand("log", sub_cmd_description="Get's the bots last few log messages.")
    async def _tail(self, ctx: InteractionContext, count: int = 10) -> None:
        await ctx.defer(ephemeral=True)
        lines = []
        current_dir = Path(__file__).parent.parent.parent
        log_loc = current_dir / "logs" / "bot.log"
        async with AIOFile(log_loc, "r") as af:
            async for line in LineReader(af):
                lines.append(line)
                if len(lines) == count + 1:
                    lines.pop(0)
        log = "".join(lines)
        if len(log) > 1500:
            with BytesIO() as file_bytes:
                file_bytes.write(log.encode("utf-8"))
                file_bytes.seek(0)
                log = File(file_bytes, file_name=f"tail_{count}.log")
                await ctx.send(content="Here's the latest log.", file=log)
        else:
            await ctx.send(content=f"```\n{log}\n```")

    @debug_info.subcommand(
        "guilds", 
        sub_cmd_description="Lists the names of the guilds the bot is in.",
    )
    async def _guild_names(self, ctx:InteractionContext) -> None:
        await ctx.defer(ephemeral=True)
        guild_list = []

        for guild in self.bot.guilds:
            guild_list.append(f"[ {guild.name} ]")

        await ctx.send(f"Guilds: {', '.join(guild_list)}")

    # @debug_info.subcommand("update", sub_cmd_description="Pulls the lastest version of the bot.")
    # async def _update(self, ctx: InteractionContext) -> None:
    #     status = await update(self.bot)
    #     if status:
    #         console = Console()
    #         with console.capture() as capture:
    #             console.print(status.table)
    #         self.logger.debug(capture.get())
    #         self.logger.debug(len(capture.get()))
    #         added = "\n".join(status.added)
    #         removed = "\n".join(status.removed)
    #         changed = "\n".join(status.changed)

    #         fields = [
    #             EmbedField("Old Commit", status.old_hash),
    #             EmbedField("New Commit", status.new_hash),
    #         ]
    #         if added:
    #             fields.append(EmbedField("New Modules", f"```\n{added}\n```"))
    #         if removed:
    #             fields.append(EmbedField("Removed Modules", f"```\n{removed}\n```"))
    #         if changed:
    #             fields.append(EmbedField("Changed Modules", f"```\n{changed}\n```"))
            
    #         embed = build_embed(
    #             "Update Status", description="Updates have been applied", fields=fields
    #         )

def setup(bot):
    BotInfo(bot)

# https://git.zevaryx.com/stark-industries/jarvis/jarvis-bot/-/blob/dev/jarvis/cogs/botutil.py
