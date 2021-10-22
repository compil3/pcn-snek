import datetime
import logging

from dis_snek.models import ( Scale, Embed, timestamp )
from dis_snek.models.application_commands import slash_command, slash_option, slash_permission, Permission

import motor.motor_asyncio as motor

import requests

from extensions import default


config = default.config()
format = "%b %d %Y %I:%M%p"

# Mongo Stuff
cluster = motor.AsyncIOMotorClient(config['mongo_connect'])
db = cluster['Nation']
collection = db['verification']

# Guild stuff
guildid = 689119429375819951
new_user = Permission(843896103686766632,1,True),


class Verification(Scale):

    @slash_command("add", description="Add yourself to the verification queue.", scope=guildid, default_permission=False)
    @slash_permission(guild_id=guildid, permissions=new_user)
    @slash_option("gamertag", "Your Xbox Gamer tag on the site.", 3, required=True)
    async def add_queue(self, ctx, gamertag:str):
        await ctx.defer(ephemeral=True)

        try:
            test_id = await collection.find_one({"_id": ctx.author.id})
            embed = Embed(title="Verification System")
            embed.set_author(name="Pro Clubs Nation", url="https://proclubsnation.com", icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png")

            if test_id is True:
                results = await collection.find_one({"_id": ctx.author.id})
                for user in results:
                    embed.description = "You are already in the queue.  Please be patient while we process requests on a first-come, first-serve basis."
                    embed.add_field(name="Status", value=user['status'])
                    embed.add_field(name="Reason", value=user['reason'])
                    embed.set_footer(text="proclubsnation.com")
                    break
            else:
                now = datetime.datetime.now()

                data = {
                    "_id": ctx.author.id,
                    "discord_name": ctx.author.user.display_name + "#" + ctx.author.user.discriminator,
                    "gamertag": gamertag,
                    "status": "In Queue",
                    "reason": "New Application",
                    "updated": now.strftime(format)
                }
                collection.insert_one(data)
                registered = await collection.find_one({"_id": ctx.author.id})
                embed.add_field(name="Status", value="You have been added to the queue.  Please be patient while we process requests on a first-come, first-server basis.")
                embed.add_field(name="\u200b", value="```Receipt```", inline=False)
                embed.add_field(name="Gamertag", value=gamertag, inline=True)
                embed.add_field(name="Status", value="New Application Submitted")
                embed.add_field(name="Date", value=registered['updated'])
    
        except Exception as e:
            logging.error(e)
        await ctx.send("A copy has been DM'd to you as well.", embeds=[embed])
        await ctx.author.send(embeds=[embed])


def setup(bot):
    Verification(bot)