import datetime
import logging
from typing import TYPE_CHECKING

import motor.motor_asyncio as motor
from naff import Embed, Extension, events, listen
from naff.api.events import MemberAdd, MemberRemove, MemberUpdate
from utils import auto_verify


# https://discord.gg/NMEvVckA
class Events(Extension):
   

    @listen()
    async def on_member_remove(self, event: MemberRemove):
        ...


    # @listen()
    # async def on_member_add(self, event: MemberAdd):
    #     new_role = 843896103686766632
    #     if new_role not in event.member.roles:
    #         await event.member.add_role(new_role, reason="Added to `New` role")
    
    @listen()
    async def on_member_update(self, event:MemberUpdate):
        new_role = 843896103686766632
        player_role = 843899510483976233
        new_user = event.before
        # when the user joins the server for the first time.
        if event.after.pending is True:
            return
        else:
            # when the user accepts the welcome screen.
            if event.after.pending is False and new_role not in event.after.roles:
                if auto_verify.autoverify(self, event.after.user.display_name) is True:
                    await event.after.add_role(player_role, "Verified, added 'Player' role")
                else:
                    await event.after.add_role(new_role, reason="Added to `New` role")
                    try:
                        await event.after.user.send("We are unable to verify your gamer tag based off your Discord name. Please verify your gamertag using `/verify <gamertag>`")
                    except:
                        new_member_channel = event.guild.get_channel(854724422572048414)
                        await new_member_channel.send(f"{event.after.user.mention} We are unable to verify your gamer tag based off your Discord name. Please verify your gamertag using `/verify <gamertag>`")


def setup(bot):
    Events(bot)
