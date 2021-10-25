import logging

import motor.motor_asyncio as motor
from dis_snek.models import listen
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.discord_objects.user import Member
from dis_snek.models.listener import listen
from dis_snek.models.scale import Scale
from extensions import default
from extensions import auto_verify

config = default.config()

cluster = motor.AsyncIOMotorClient(config["mongo_connect"])
db = cluster["Nation"]
collection = db["registered"]
verify = auto_verify.verify


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


    @listen()
    async def on_member_remove(self, event):
        ...

    @listen()
    async def on_member_update(self, event):
        role_id = 843896103686766632

        if event.before.pending and event.after.pending is True:
            pass
        elif event.after.pending is False and event.before.pending is True:
            if verify(event.after.display_name) is False:
                embed = Embed(
                    title="Welcome to Pro Clubs Nation Discord",
                    description="Unfortunately your Discord username does not match any records.  Therefore you will have to add yourself to our verification queue by typing **/add [GamerTag]** inside of **#new-member-verification** and waiting until you are verified.  Thank you for your patience.",
                )
            else:
                embed = Embed(
                    title="Welcome to Pro Clubs Nation Discord",
                    description="You have been automatically verified as your Discord name matches our records.  If this is incorrect please let a Moderator know.  Failure to do so will result in termination of access to our Discord.  Thank you and play nice.",
                )              
                await event.after.add_role(role_id)
            await event.after.send(embeds=[embed])
        else:
            pass

    @listen()
    async def on_member_add(self, event):
        ...


def setup(bot):
    Events(bot)
