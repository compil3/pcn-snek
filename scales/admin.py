import logging
import pathlib
from os import listdir

import motor.motor_asyncio as motor
import psutil
from dis_snek.errors import ExtensionNotFound, ScaleLoadException
from dis_snek.models import Embed, Scale
from dis_snek.models.application_commands import (OptionTypes, Permission,
                                                  component_callback,
                                                  slash_command, slash_option,
                                                  slash_permission)
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.components import Select, SelectOption
from extensions import default, globals

config = default.config()
format = "%b %d %Y %I:%M%p"

# Mongo Stuff
cluster = motor.AsyncIOMotorClient(config['mongo_connect'])
db = cluster['Nation']
collection = db['verification']

guild_id = 689119429375819951
staff_only = Permission(842505724458172467, 1, True),


class Admin(Scale):
    # globals.init()
    scales_list = []
    path = pathlib.Path.cwd()
    for file in path.glob("scales/*.py"):
        scales_list.append(file.stem)

    @slash_command("reload", "Reload all Scales", scopes=[guild_id,], default_permission=False)
    @slash_permission(guild_id=guild_id, permissions=staff_only)
    @slash_option("scale", description="Scale to reload", opt_type=OptionTypes.STRING, required=False)
    @slash_option("reload_all", description="Reload all Scales", opt_type=OptionTypes.BOOLEAN, required=False)
    async def reload(self, ctx, **kwargs):
        embed = Embed(title="Reloading all Scales!", color=0x808080)
        
        print(kwargs)
        for filename in listdir("./scales"):
            
            if kwargs is None:        
                if filename.endswith(".py") and not filename.startswith("_"):
                    try:
                        self.bot.regrow_scale(f"scales.{filename[:-3]}")
                        print(f"Loaded scales.{filename[:-3]}")
                        logging.info(f"scales.{filename[:-3]} loaded.")
                        embed.add_field(name=f"Reloaded: ``{filename}``", value="\uFEFF", inline=False)
                    except Exception as e:
                        print(f"Failed to load scale {filename[:-3]}: {e}")
                        embed.add_field(name=f"Failed to load ``{filename}``", value=e, inline=False)
            elif kwargs == filename:
                if ".py" not in kwargs:
                    module = kwargs + ".py"
                if module == filename:
                    self.bot.regrow_scale(f"scales.{filename[:-3]}")
                    print(f"Reloaded {filename}")
                    return
                else:
                    pass

        await ctx.send(embeds=[embed], ephemeral=True)

    @reload.error
    async def load_error(self, e: ExtensionNotFound, *args, **kwargs):
        logging.error(f"load.error caught failure: {e}\n{args=}\n{kwargs=}")

    # TODO: add a reload single scale command

    @slash_command("scales", description="Staff Only", scopes=[guild_id,], default_permission=False)
    @slash_permission(guild_id=guild_id, permissions=staff_only)
    async def scale_builder(self, ctx: InteractionContext, **kwargs):
        await ctx.defer(ephemeral=True)
        try:
            selection = Select(
                placeholder="Select a Scale to reload",
                min_values=1,
                max_values=1,
                custom_id="ScalesList",
            )
            for file in Admin.scales_list:
                selection.add_option(
                    SelectOption(label=file, value=file, default=False)
                )
            await ctx.send(f"Testing list", components=selection)
        except Exception as e:
            print(e)

    @component_callback("ScalesList")
    async def scalelist_callback(self, ctx: InteractionContext, **kwargs):
        await ctx.defer(ephemeral=True)
        selected_scale = ctx.data["data"]["values"][0]
        embed = Embed(title=f"Attempting to reload {selected_scale}", color=0x808080)
        if selected_scale in Admin.scales_list:
            try:
                self.bot.regrow_scale(f"scales.{ctx.data['data']['values'][0]}")
                embed.add_field(name=f"Reloaded Scale", value=selected_scale, inline=False)
                await ctx.edit_origin(embeds=[embed])
            except ScaleLoadException:
                self.bot.grow_scale(f"scales.{ctx.data['data']['values'][0]}")
                embed.add_field(name=f"Reloaded Scale", value=selected_scale, inline=False)
                await ctx.edit_origin(embeds=[embed])
        else:
                print("Nothing Worked.")

    # @slash_command("stats", "Check bot statistics", scopes=[guild_id,], default_permission=False)
    # @slash_permission(guild_id=guild_id, permissions=staff_only)
    # async def stats(self, ctx):
    #     await ctx.defer(ephemeral=True)
    #     seconds = "0"
    #     minutes = "0"
    #     hours = "0"
    #     if globals.time_seconds <= 9:
    #         seconds = "0" + str(globals.time_seconds)
    #     elif globals.time_seconds > 9:
    #         seconds = str(globals.time_seconds)
    #     if globals.time_minutes <= 9:
    #         minutes = "0" + str(globals.time_minutes)
    #     elif globals.time_minutes > 9:
    #         minutes = str(globals.time_minutes)
    #     if globals.time_hours <=9:
    #         hours = "0" + str(globals.time_hours)
    #     elif globals.time_hours > 9:
    #         hours = str(globals.time_hours)
        

    #     uptime = "Days: " + str(globals.time_days) + "\n" + "Time: " + hours + ":" + minutes + ":" + seconds
    #     embed = Embed(title="Bot Statistics", color=0x808080)
    #     embed.add_field(name="Uptime:", value=uptime, inline=False)
    #     embed.add_field(name="Latency", value=f"{round(self.bot.latency*100,3)}ms", inline=False)
    #     # embed.add_field(name="Hours:", value=str(globals.time_hours), inline=True)
    #     # embed.add_field(name="Minutes:", value=str(globals.time_minutes), inline=True)
    #     # embed.add_field(name="Seconds:", value=str(globals.time_seconds), inline=False)
    #     embed.add_field(name="CPU", value=f"{psutil.cpu_percent()}%", inline=True)
    #     embed.add_field(name="RAM", value=f"{psutil.virtual_memory()[2]}%", inline=True)
    #     await ctx.send(embeds=[embed], ephemeral=True)





def setup(bot):
    Admin(bot)
