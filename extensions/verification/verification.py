import datetime
import logging

from beanie import Document
from naff import (Client, Embed, Extension, Permissions, slash_command,
                  slash_option, listen)
from utils import auto_verify

format = "%b %d %Y %I:%M%p"

class VerificationQueue(Document):
    discord_id: int
    discord_name: str
    gamertag: str
    status: str
    reason: str
    updated: str

    class Collection:
        name = "verification_queue"

class UserRegistration(Document):
    user_id: int
    discord_full_name: str
    registered_gamer_tag: str
    pcn_url: str
    registered_date: str

    class Collection:
        name = "discord_registered"


class Verification(Extension):

    @slash_command(
        "verify",
        description="Add yourself to the verification queue.",
        scopes=[
            689119429375819951,
        ],
        default_member_permissions=Permissions.USE_APPLICATION_COMMANDS
    )
    @slash_option("gamertag", "Your Xbox Gamer tag on the site.", 3, required=True)
    async def add_queue(self, ctx, gamertag: str):
        await ctx.defer(ephemeral=True)
        try:
            embed = Embed(title="Verification System")
            embed.set_author(
                name="Pro Clubs Nation",
                url="https://proclubsnation.com",
                icon_url="https://proclubsnation.com/wp-content/uploads/2020/08/PCN_logo_Best.png",
            )
            # Query the databases for the gamer tag (find_user) and discord_id (registered_user)
            registered_user = await UserRegistration.find_one(UserRegistration.user_id == ctx.author.id)
            find_user = await VerificationQueue.find_one(VerificationQueue.discord_id == ctx.author.id)

            # Check if user is found on website
            if auto_verify.autoverify(self, gamertag) is True:
                #if the discord_id is found in the registration db, then just assign roles and send a Welcome message.
                if registered_user is not None:
                    await ctx.author.add_role(843899510483976233, "Verified, added 'Player' role")
                    await ctx.author.remove_role(843896103686766632, "Removed from `New` role")
                    await ctx.send(f"{ctx.author.mention},\nWelcome to PCN Discord!")
                #if the discord_id is not found in the registration db, then add the user to the registration db and assign roles.
                else:

                    registering_user = UserRegistration(
                        user_id = ctx.author.id,
                        discord_full_name = ctx.author.user.display_name + "#" + ctx.author.user.discriminator,
                        registered_gamer_tag=gamertag,
                        pcn_url=self.bot.config.urls.players.format(gamertag),
                        registered_date=datetime.now().strftime(format),
                    )
                    await registering_user.save()
                    await ctx.author.add_role(843899510483976233, "Verified, added 'Player' role")
                    await ctx.author.remove_role(843896103686766632, "Removed from `New` role")
                    embed.add_field("You have been successfully verified and 0registered.")
            # If the user doesn't exist on the website, add user to Queue DB, and register the discord_id
            else:
                #if the discord_id is found, then send the user a message telling they are in queue
                if find_user is not None:
                    embed.description = "You are already in the queue.  Please be patient while we process requests on a first-come, first-serve basis."
                    embed.add_field(name="Status", value=find_user.status, inline=False)
                    embed.add_field(name="Reason", value=find_user.reason, inline=False)
                    embed.set_footer(text="proclubsnation.com")
                #if the discord_id is not found, add user to verification queue and register the discord_id.
                else:
                    now = datetime.datetime.now()
                    vqueue_user = VerificationQueue(
                        discord_id=ctx.author.id,
                        discord_name=ctx.author.user.display_name + "#" + ctx.author.user.discriminator,
                        gamertag=gamertag,
                        status="New",
                        reason="New Applicant",
                        updated=now.strftime(format),
                    )
                    registering_user = UserRegistration(
                        user_id = ctx.author.id,
                        discord_full_name = ctx.author.user.display_name + "#" + ctx.author.user.discriminator,
                        registered_gamer_tag=gamertag,
                        pcn_url=self.bot.config.urls.players.format(gamertag),
                        registered_date=datetime.now().strftime(format),
                    )
                    await vqueue_user.save()
                    await registering_user.save()
                    embed.add_field(
                        name="Status",
                        value="You have been added to the queue, and the requested gamer tag has been registered with the bot.\nPlease be patient while we process requests on a first-come, first-server basis.",
                    )
                    embed.add_field(name="Gamertag", value=gamertag, inline=True)
                    embed.add_field(name="Status", value="New Application Submitted")
                    embed.add_field(name="Date", value=now.strftime(format), inline=True)

        except Exception as e:
            logging.error(e)

        await ctx.author.send(embeds=[embed])
        await ctx.send(embeds=[embed])

    @slash_command(
        "check",
        description="Check the status of your Discord application",
        scopes=[
            689119429375819951,
        ],
        default_member_permissions=Permissions.USE_APPLICATION_COMMANDS
    )
    # @slash_permission(guild_id=guildid, permissions=new_user)
    async def check(self, ctx):
        await ctx.defer(ephemeral=True)
        _status = None
        embed = None
        try:
            applicant_status = await VerificationQueue.find_one(VerificationQueue.discord_id == ctx.author.id)

            if applicant_status.status == "Denied":
                _status = f"**Status** :no_entry: **{applicant_status.status}"
                _reason = applicant_status.reason
                _updated = applicant_status.updated
            else:
                _status = f":warning:  **Verification {applicant_status.status}**"
                _reason = f"**{applicant_status.reason}**"
                _updated = applicant_status.updated

            embed = Embed(title="PCN Discord Verification Status", description=_status)
            embed.add_field(name="**Reason**", value=_reason, inline=False)
            embed.add_field(name="Last Updated", value=_updated, inline=False)
        except Exception as e:
            logging.error(e)
        await ctx.send(embeds=[embed])
  
def setup(bot):
    Verification(bot)
    bot.add_model(VerificationQueue)
    bot.add_model(UserRegistration)
