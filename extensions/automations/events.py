import datetime
import logging
from typing import TYPE_CHECKING

import motor.motor_asyncio as motor
from naff import Embed, Extension, events, listen
from naff.api.events import MemberAdd, MemberRemove, MemberUpdate, MessageCreate
from utils import auto_verify


# https://discord.gg/NMEvVckA
class Events(Extension):
   
    @listen()
    async def on_member_update(self, event:MemberUpdate):
        """Automatically checks if a joining user is already verified on the website

        Args:
            event (MemberUpdate): _description_
        """
        player_role = 843899510483976233
        new_role = 843896103686766632

        if event.after.pending is True:
            return
        if new_role not in event.after.roles:
            if auto_verify.autoverify(self, event.after.user.display_name):
                await event.after.add_role(player_role, "Verified, added 'Player' role")
            elif new_role not in event.after.roles:
                try:
                    await event.after.user.send("We are unable to verify your gamer tag based off your Discord name. Please verify your gamertag using `/verify <gamertag>`")
                    await event.after.add_role(843896103686766632, "Added 'New' role")
                except:
                    new_member_channel = event.guild.get_channel(840012242950684692)
                    await new_member_channel.send(f"{event.after.user.mention} We are unable to verify your gamer tag based off your Discord name. Please verify your gamertag using `/verify <gamertag>`", delete_after=7)
                    await event.after.add_role(843896103686766632, "Added 'New' role")
        else: 
            pass

    @listen()
    async def on_message_create(self, event: MessageCreate):
        """Automatically deletes any message that is in specific channel
        
        Args:
            event (MessageCreate): _description_
        """

        message = event.message

        if message.type.name == "PRIVATE" or message.channel.type.name == "DM":
            return
        if message.channel.id != 840012242950684692:
            pass
        else:

            if message.author.has_role(842505724458172467) or message.author.bot:
                pass
            else:
                await message.delete()

def setup(bot):
    Events(bot)
