import asyncio
import logging
import re
import time
from asyncio import tasks

import aiohttp
import httpx
import psutil
import requests
from dis_snek.models import Embed, Scale
from dis_snek.models.application_commands import (Permission, slash_command,
                                                  slash_permission)
from extensions import default, globals

config = default.config()

guild_id =689119429375819951
staff_only =Permission(842505724458172467, 1, True),


class BotInfo (Scale):
   
    
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
            if "?slug={}" in value:
                value = value.replace("?slug={}", "")
            elif "teams" in sites:
                value = value.replace("/v2/teams", "/v2/teams?slug=ac-milan")
            urls.append(value)
        resps = await asyncio.gather(*map(BotInfo.get_async, urls))
        for data in resps:
            if "teams" in str(data.request.url):
                team_delay = round(data.elapsed.total_seconds(),2)
            elif "players" in str(data.request.url):
                player_delay = round(data.elapsed.total_seconds(),2)
            elif "tables" in str(data.request.url):
                table_delay = round(data.elapsed.total_seconds(),2)
        
        if globals.time_seconds <= 9:
            seconds = "0" + str(globals.time_seconds)
        elif globals.time_seconds > 9:
            seconds = str(globals.time_seconds)
        if globals.time_minutes <= 9:
            minutes = "0" + str(globals.time_minutes)
        elif globals.time_minutes > 9:
            minutes = str(globals.time_minutes)
        if globals.time_hours <=9:
            hours = "0" + str(globals.time_hours)
        elif globals.time_hours > 9:
            hours = str(globals.time_hours)
        
        
        uptime = "Days: " + str(globals.time_days) + "\n" + "Time: " + hours + ":" + minutes + ":" + seconds
        embed = Embed(title="Bot Statistics", color=0x808080)
        embed.add_field(name="\u200b", value="```Hardware```", inline=False)
        embed.add_field(name="Uptime:", value=uptime, inline=False)
        embed.add_field(name="CPU", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.add_field(name="RAM", value=f"{psutil.virtual_memory()[2]}%", inline=True)
        embed.add_field(name="\u200b", value="```API```", inline=False)
        embed.add_field(name="Bot Response", value=f"```{round(self.bot.latency * 100, 2)}s ```", inline=True)
        embed.add_field(name="Player API", value=f"```{player_delay}```", inline=True)
        embed.add_field(name="Table API", value=f"```{table_delay}```", inline=True)
        embed.add_field(name="Teams API", value=f"```{team_delay}```", inline=True)
        await ctx.send(embeds=[embed])

def setup(bot):
    BotInfo(bot)
