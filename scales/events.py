import logging

from dis_snek.models import listen
from dis_snek.models.scale import Scale
from dis_snek.models.listener import listen
from dis_snek.models.discord_objects.embed import Embed

import motor.motor_asyncio as motor

from extensions import default

config = default.config()

cluster = motor.AsyncIOMotorClient(config['mongo_connect'])
db = cluster["Nation"]
collection = db["registered"]

class Events(Scale):

    @listen()
    async def on_message_create(self, event):

        message = event.message

        if message.type.name == "PRIVATE" or message.channel.type.name == "DM":
            return
        if message.channel.id != 900790928690790400:
            pass
        else:

            if await message.author.has_role(842505724458172467) or message.author.bot:
                pass
            else:
                await message.delete()

    @listen()
    async def on_message_delete(self, event):
        message = event.message
        print(f"\n\n{message.content}")
        if message.type.name == "PRIVATE":
            return
        elif message.type.name == "DEFAULT":
            if message.author.id is self.bot.user.id:
                ...
            else:
                logging.info(
                    f"\n{message.author.display_name} deleted a message.\nContent: {message.content}"
                )
    

    # TODO: Add message on member join
    # @listen()
    # async def on_raw_member_remove(self, event):
    #     print(event)
    #     # print(f"\n\n{event.guild.name}")
    #     # print(f"\n\n{event.guild.id}")
    
    
    # @listen()
    # async def on_raw_member_add(self, event):
    #     print(event)
    #     print(f"\n\n{event.guild.name}")
    #     print(f"\n\n{event.guild.id}")
    # # when a member joins send them an embed

    # # @listen()
    # # async def raw_guild_member_add(self, event: GuildEvent):
    # #         print(event)
    # #         print(event.member)


def setup(bot):
    Events(bot)
