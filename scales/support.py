from dis_snek import (
    message_command,
    Scale,
    MessageContext,
    Button,
    ButtonStyles,
    InteractionContext,
    AutoArchiveDuration,
    ChannelTypes,
    listen,
    slash_command,
)
from dis_snek.models.discord import Guild
thread_channel_id = 956330226806292510 # 956039958290911322


class Support(Scale):
    @message_command()
    async def init(self, ctx: MessageContext):
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

    async def create_thread(self, ctx: InteractionContext):
        channel = await self.bot.fetch_channel(thread_channel_id)

        thread = await channel.create_thread_without_message(
            name=f"{ctx.author.display_name}'s Support Thread",
            auto_archive_duration=AutoArchiveDuration.ONE_HOUR,
            reason="Bot Support Thread",
            thread_type=ChannelTypes.GUILD_PRIVATE_THREAD,
        )
        await thread.send(
            f"Hi {ctx.author.mention}.  Welcome to your support thread!  Please explain your issue here and someone will assist you shortly."
        )
        
        await ctx.send(f"Your support thread has been created.  You can view it here: {thread.mention}", ephemeral=True)

    
    @listen()
    async def on_button(self, b):
        ctx = b.context
        if ctx.custom_id == "create_support_thread":
            await ctx.defer(ephemeral=True)
            await self.create_thread(ctx)

    @slash_command(
        "support-thread",
        sub_cmd_name="start",
        sub_cmd_description="Start a support thread",
    )
    async def support_start(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        await self.create_thread(ctx)

    @listen()
    async def on_thread_create(self, thread):
        print("Thread Created")

    @listen()
    async def on_thread_update(self, thread):
        print("Thread Closed")
def setup(bot):
    Support(bot)
    