from naff import (AutoArchiveDuration, Button, ButtonStyles, ComponentContext,
                  Extension, InteractionContext, Modal, ModalContext,
                  ParagraphText,PrefixedContext, component_callback,
                  prefixed_command, slash_command, ChannelTypes, ShortText, Permissions)
from naff.models.naff.application_commands import modal_callback

thread_channel_id = 956178792378953778 # 956039958290911322


class Support(Extension):
    @prefixed_command()
    async def init(self, ctx: PrefixedContext):
        if ctx.author.id == 111252573054312448:
            await ctx.message.delete()
            await ctx.send(
                "To get support from our staff, please press the button below.",
                components=[
                    Button(
                        style=ButtonStyles.BLURPLE,
                        label="Create Support Thread",
                        custom_id="create_support_thread",
                        emoji="❔",
                    )
                ],
            )

    @modal_callback("support_thread_modal")
    async def create_thread(self, ctx: ModalContext):
        await ctx.defer(ephemeral=True)

        channel = await self.bot.fetch_channel(thread_channel_id)
        description = ctx.responses.get("description")
        additional = ctx.responses.get("additional")
        

        thread = await channel.create_thread_without_message(
            name=f"{ctx.author.display_name}'s Support Thread",
            auto_archive_duration=AutoArchiveDuration.ONE_HOUR,
            reason="Bot Support Thread",
            thread_type=ChannelTypes.GUILD_PRIVATE_THREAD,
        )
        await thread.send(
            f"Welcome to your support thread {ctx.author.mention} - Someone will help you shortly."
        )
        await thread.send(f"**Provided information:**\n{description}")
        if additional:
            await thread.send(f"**Additional information:**\n{additional}")
        await ctx.send(f"Your support thread has been created here: {thread.mention}", ephemeral=True)

    @component_callback("create_support_thread")
    async def support_thread_button(self, ctx: ComponentContext):
        await ctx.send_modal(
            Modal(
                "Support Thread Wizard",
                custom_id="support_thread_modal",
                components=[
                    ShortText(
                        label="Describe your problem",
                        custom_id="description",
                        placeholder="Please provide a summary of your problem.",
                        required=True,
                    ),
                    ParagraphText(
                        label="Additional information",
                        custom_id="additional",
                        placeholder="Please provide any additional information.",
                        required=False,
                    )
                ]
            )
        )

    @slash_command(
        "support_thread",
        # sub_cmd_name="start", 
        # sub_cmd_description="Start a support thread",
        scopes=[689119429375819951, 442081251441115136],
        default_member_permissions=Permissions.USE_APPLICATION_COMMANDS
    )
    async def support_start(self, ctx: InteractionContext):
        await self.support_thread_button(ctx)
    
def setup(bot):
    Support(bot)
    