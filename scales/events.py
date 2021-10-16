import logging

from dis_snek.models import listen
from dis_snek.models.scale import Scale
from dis_snek.models.listener import listen


class Events(Scale):
    @listen()
    async def on_message_create(self, event):

        message = event.message
        if message.type.name == "PRIVATE" or message.channel.type.name == "DM":
            return
        elif message.type.name == "DEFAULT":
            if (
                await message.author.has_role(842505724458172467)
                or await message.author.bot
            ):
                ...
            else:
                await message.delete()

    @listen()
    async def on_message_delete(self, event):
        message = event.message
        print(dir(message.author))
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


def setup(bot):
    Events(bot)
