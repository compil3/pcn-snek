from datetime import datetime
from dis_snek.models.snek.application_commands import (
    PermissionTypes,
    slash_command,
    Permission,
    component_callback
)
from dis_snek.models import Scale, Embed
from dis_snek.models.discord import Guild
from dis_snek.models.discord.components import Button, ButtonStyles, ActionRow
from dis_snek.models.discord.enums import ButtonStyles
from dis_snek.models.snek.context import ComponentContext,  ModalContext
from dis_snek.models.discord.color import MaterialColors
from dis_snek.ext.paginators import Paginator
from dis_snek.models.discord.modal import Modal, ShortText, ParagraphText
import logging
from typing import TYPE_CHECKING

from beanie import Document
from config import load_settings
if TYPE_CHECKING:
    from main import Bot


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

#PCN Roles
# Admin - 552702041395298324
# Roster Admin - 543563725630865417
# player admin - 442082962826199041
# Moderator - 608012366197686286
# Owner - 442082486022045697
# Discord Management - 545392640884211712


class Queue(Scale):
    
    bot: "Bot"
    
    @slash_command(
        "queue", 
        "Discord Verification Queue", 
        scopes=[
            689119429375819951,
        ], 
        default_permission=False, 
        permissions=[
            Permission(842505724458172467, 689119429375819951, PermissionTypes.ROLE, True),
            # Permission(608012366197686286, )
        ],
    )
    async def queue(self, ctx:ComponentContext):
        await ctx.defer(ephemeral=True)
        components: list[ActionRow]= [
            ActionRow(
                Button(
                    style=ButtonStyles.RED,
                    label="Denied Queue", 
                    custom_id="denied_queue"
                ),
                Button(
                    style=ButtonStyles.GREEN,
                    label="New/Waiting",
                    custom_id="new_waiting_queue"
                )
            )
        ]
        await ctx.send("Select an option.", components=components)

    @component_callback("denied_queue")
    async def denied_queue(self, ctx:ComponentContext):
        await ctx.defer(edit_origin=True)

        embeds = []

        result = await VerificationQueue.find(VerificationQueue.status == "Denied").to_list()
        embed = Embed(color=MaterialColors.GREEN)
        for user in result:
            embed = Embed("Verification Queue", description=f"Gamertag: `{user.discord_name}`")
            embed.add_field("Gamertag", user.gamertag, inline=False)
            embed.add_field("User Id", user.discord_id, inline=False)
            embed.add_field(name="Reason", value=user.reason, inline=False)
            embed.add_field(name="Updated", value=user.updated, inline=False)
            embeds.append(embed)
        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        paginator.callback= self.show_edit
        paginator.callback_button_emoji="<:memo:956893316820127745>"
        paginator.show_callback_button=True
        
        await paginator.send(ctx)


    async def show_edit(self, ctx):
        # config = load_settings()
        # new_role = Bot.config.roles.new
        #TODO: Add config import for roles instead of hardcoding
        player_role_id= 843899510483976233

        _discord_id = ctx.message.embeds[0].fields[1].value
        try:
            result = await VerificationQueue.find_one(VerificationQueue.discord_id == int(_discord_id))
        except Exception as e:
            logging.error(e)
            await ctx.send(f"An error occured while searching. Please try again later.\nReport this error to Spillshot.\n{e}")
        
        if result is not None:
            edit_user = Modal(
                title=f"Edit user {result.discord_name} | {result.gamertag}",
                components=[
                    ShortText(
                        label="Queue Status (Enter Approved or Denied Only)",
                        value=f"Current status: {result.status}",
                        custom_id="status"
                    ),
                    ParagraphText(
                        label="Status Reason",
                        value=f"Current reason: {result.reason}",
                        custom_id="reason"
                    )
                ]
            )
            await ctx.send_modal(edit_user)
            _response: ModalContext = await ctx.bot.wait_for_modal(edit_user)
            if _response.responses is not None:
                guild_member = await Guild.fetch_member(ctx.guild, int(_discord_id))
                if _response.responses["status"] == "Approved":
                    try:
                        await guild_member.add_role(player_role_id)
                        if 843896103686766632 in guild_member.roles:
                            await guild_member.remove_role(843896103686766632, "Removed from `New` role")
                        if player_role_id not in guild_member.roles:
                            await guild_member.add_role(player_role_id, reason="Added `Player` role by the bot.")

                    except Exception as e:
                        logging.error(e)

                    

                result.status = _response.responses["status"]
                result.reason = _response.responses["reason"]
                time_now = datetime.now().strftime(format)
                # await result.save()
                embed = Embed("Verification Queue Updated", description=f"Updated for ``{result.discord_name}``")
                embed.add_field("Gamertag", result.gamertag, inline=False)
                embed.add_field("User Id", result.discord_id, inline=False)
                embed.add_field("Status", _response.responses.get("status"), inline=False)
                embed.add_field("Reason", _response.responses.get("reason"), inline=False)
                embed.add_field("Updated", time_now, inline=False)
                await _response.send(embeds=[embed], components=[], ephemeral=True)
            else:
                await ctx.send(f"User {result.discord_name} | {result.gamertag} has not been updated.")
       
def setup(bot):
    Queue(bot)
    bot.add_model(VerificationQueue) 