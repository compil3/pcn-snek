import logging
from dis_snek.models.application_commands import PermissionTypes
from dis_snek.models.context import InteractionContext
from dis_snek.models.enums import CommandTypes
import requests
import re
import motor.motor_asyncio as moto

from dis_snek.models import (Embed, Scale, Permission, context_menu, slash_command, slash_permission, MaterialColors, slash_option, check)

from extensions import default


config = default.config()

default_player_url = config['urls']['find_player']

guildid = 689119429375819951

# Player permission
user_perm = [Permission(843899510483976233,PermissionTypes.ROLE, True)]

class PlayerStats(Scale):
    @slash_command("stats", "Look up PCN Stats for yourself or someone else.", scopes=[guildid], default_permission=False)
    @slash_permission(guild_id=guildid, permissions=user_perm)
    @slash_option("gamertag","Enter a Gamertag", 3, required=False)
    async def stats(self, ctx: InteractionContext, gamertag:str):
        """
        Look up PCN Stats for yourself or someone else.
        """
        await ctx.defer(ephemeral=True)
        post = []
        if gamertag is None:
            gamertag = ctx.author.display_name
            try:
                post = self.D_Embed(gamertag, False)
                if post is not None:
                   ...
                else:
                    await ctx.send("Unable to retreive your stats.  If you discord name does not match your gamertag, you will need to use /stats [gamertag].") 
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

    
    @context_menu("Stats", context_type=CommandTypes.USER, scopes=[guildid], default_permission=False, permissions=user_perm)
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
            post = self.D_Embed(gamertag, False)
            if post is not None:
                ...
            else:
                await ctx.send("Unable to retreive your stats.  If you discord name does not match your gamertag, you will need to use /stats [gamertag].") 
                return
        except Exception as e:
            logging.ERROR(e)
    
