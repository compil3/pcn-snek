import logging
import datetime
from dis_snek.models import listener, Timestamp

import motor.motor_asyncio as motor
from dis_snek.models import listen
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.discord_objects.user import Member
from dis_snek.models.listener import listen
from dis_snek.models.scale import Scale
from dis_snek.models.events import MessageCreate, MessageDelete, MessageUpdate, MemberAdd, MemberRemove, MemberUpdate
from extensions import default
from extensions import auto_verify

config = default.config()

cluster = motor.AsyncIOMotorClient(config["mongo_connect"])
db = cluster["Nation"]
collection = db["registered"]
verify = auto_verify.verify


class Events(Scale):
    @listen()
    async def on_message_create(self, event: MessageCreate):

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
    async def on_message_delete(self, event: MessageDelete):
        message = event.message
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
    async def on_member_remove(self, event: MemberRemove):
        ...

    @listen()
    async def on_member_update(self, event: MemberUpdate):
        role_id = 843896103686766632
        before = event.before
        after = event.after
        if event.before.pending and event.after.pending:
            pass
        elif before.pending and not after.pending:
            if not verify(event.after.display_name):
                embed = Embed(
                    title="Welcome to Pro Clubs Nation Discord",
                    description="Unfortunately your Discord username does not match any records.  Therefore you will have to add yourself to our verification queue by typing **/add [GamerTag]** inside of **#new-member-verification** and waiting until you are verified.  Thank you for your patience.",
                )
            else:
                embed = Embed(
                    title="Welcome to Pro Clubs Nation Discord",
                    description="You have been automatically verified as your Discord name matches our records.  If this is incorrect please let a Moderator know.  Failure to do so will result in termination of access to our Discord.  Thank you and play nice.",
                )
                await after.add_role(role_id)
            await after.send(embeds=[embed])
            

    @listen()
    async def on_member_add(self, event):
        ...


def setup(bot):
    Events(bot)
