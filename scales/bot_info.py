import asyncio
import datetime
import io
import platform
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import Counter

import httpx
import psutil
from dis_snek.const import __py_version__, __version__
from dis_snek.errors import CommandCheckFailure
from dis_snek.models import Embed, MaterialColors, Scale, Timestamp, check
from dis_snek.models.application_commands import (Permission, slash_command,
                                                  slash_permission)
from dis_snek.models.command import message_command
from dis_snek.models.context import InteractionContext, MessageContext
from dis_snek.models.enums import Intents
from dis_snek.utils.cache import TTLCache
from extensions import default, globals

config = default.config()

guild_id =689119429375819951
staff_only =Permission(842505724458172467, 1, True),


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

class BotInfo (Scale):
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

    @slash_command("info", description="Check bot latency", scopes=[guild_id, ], default_permission=False)
    @slash_permission(guild_id=guild_id, permissions=staff_only)
    async def info(self, ctx):
        await ctx.defer(ephemeral=True)
        urls = []
        seconds = "0"
        minutes = "0"
        hours = "0"
        for sites, value in config['urls'].items():
            match sites:
                case "find_player":
                    value.format("Spillshot")
                case "teams":
                    value = value.replace("/v2/teams", "/v2/teams?slug=ac-milan")
            urls.append(value)
        try:
            resps = await asyncio.gather(*map(BotInfo.get_async, urls))
            for data in resps:
                if "teams" in str(data.request.url):
                    team_delay = round(data.elapsed.total_seconds(),2)
                elif "players" in str(data.request.url):
                    player_delay = round(data.elapsed.total_seconds(),2)
                elif "tables" in str(data.request.url):
                    table_delay = round(data.elapsed.total_seconds(),2)
        except httpx.ConnectError:
            return await ctx.send("Could not connect to the API. Please try again later.")

        uptime = datetime.datetime.now() - self.bot.start_time
        e = self.D_Embed("Information")
        e.add_field(name="CPU", value=f"**{psutil.cpu_count(logical=False)} | {psutil.cpu_percent()}%**", inline=True)
        
        e.add_field(name="RAM", value=f"**{psutil.virtual_memory().percent}**%", inline=True)
        e.add_field("Operating System", platform.platform())
        e.add_field("Version Info", f"Dis-Snek@{__version__}  |  Py@{__py_version__}")
        e.add_field("Start Time", f"{Timestamp.fromdatetime(self.bot.start_time)}\n({strf_delta(uptime)}) ago")

        privileged_intents = [ i.name for i in self.bot.intents if i in Intents.PRIVILEGED]
        if privileged_intents: e.add_field("Intents", " | ".join(privileged_intents))
        e.add_field("Loaded Scales", ",".join(self.bot.scales))       

        e.add_field(name="\u200b", value="**API**", inline=False)
        e.add_field(name="Bot", value=f"```{round(self.bot.latency * 100, 2)}s ```", inline=True)
        e.add_field(name="Player API", value=f"```{player_delay}```", inline=True)
        e.add_field(name="\u200b", value="\u200b", inline=True)

        e.add_field(name="Table API", value=f"```{table_delay}```", inline=True)
        e.add_field(name="Teams API", value=f"```{team_delay}```", inline=True)
        await ctx.send(embeds=[e]) 


def setup(bot):
    BotInfo(bot)
