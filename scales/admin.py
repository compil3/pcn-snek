from os import listdir

from dis_snek.models.application_commands import Permission, component_callback, slash_command, slash_option, slash_permission
from dis_snek.models import ( Scale, Embed,)
from dis_snek.errors import ExtensionNotFound, ScaleLoadException
from dis_snek.models.discord_objects.components import Button, ActionRow, Select, SelectOption
from dis_snek.models.context import InteractionContext


import logging
import sys

guild_id = 689119429375819951
admin_perm = [Permission(842505724458172467, 1, True)]
class Admin(Scale):
    # FIXME: fix reload command
    @slash_command("reload", description="Reload all Scales", scope=guild_id)
    @slash_permission(guild_id=guild_id, permissions=admin_perm)
    @slash_option("scale", "Scale to reload", 3, required=False)
    @slash_option("reload_all", "Reload all Scales", 5, required=False)
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
    async def reload_error(self, e, *args, **kwargs):
        logging.ERROR(f"{args=}\n\n{kwargs=}")

    @slash_command("load", description="Reload a single Scale", scope=guild_id)
    @slash_permission(permissions=admin_perm, guild_id=guild_id)
    @slash_option("scale", "Scale to load/reload", 3, required=True, choices=None)
    async def load(self, ctx, scale: str):
        embed = Embed(title=f"Attempting to reload {scale}", color=0x808080)
        try:
            if ".py" not in scale:
                module =  scale + ".py"
            else:
                ...
            for scale_file in listdir("./scales"):
                if module == scale_file:
                    self.bot.regrow_scale(f"scales.{scale_file[:-3]}")
                    embed.add_field(name="Loaded {scale}", value="\uFEFF", inline=False)
                    await ctx.send(embeds=[embed], ephemeral=True)
                else:
                    pass
        except ExtensionNotFound as ef:
            logging.error(f"Extension {module} has not been found: {ef}.")

    
    @load.error
    async def load_error(self, e: ExtensionNotFound, *args, **kwargs):
        logging.error(f"load.error caught failure: {e}\n{args=}\n{kwargs=}")

    #TODO: add a reload single scale command

    @slash_command("scales", description="List all Scales", scope=guild_id)
    async def scale_builder(self, ctx: InteractionContext, **kwargs):
        await ctx.defer(ephemeral=True)
        
        try:
            selection = Select(placeholder="Select a Scale to reload", min_values=1, max_values=1, custom_id="ScalesList")
            for file in BuildScales():
                selection.add_option(SelectOption(label=f"{file}", value=file, default=False))
            await ctx.send(f"Testing list", components=selection)
        except Exception as e:
            print(e)

    @component_callback(custom_id="ScalesList")
    async def scalelist_callback(self, ctx, **kwargs):
        scales = BuildScales()
        if ctx.data['data']['values'][0] in scales:
            self.bot.regrow_scale(f"scales.{ctx.data['data']['values'][0]}.py")
        else:
            print("Nothing Worked.")

#TODO: Pass relative path in list
def BuildScales():
    scale_list = []
    try:
        for scale_file in listdir("./scales"):
            if scale_file.endswith(".py") and not scale_file.startswith("_"):
                scale_list.append(scale_file[:-3])
            else:
                pass
    except Exception as e:
        print(e)
    
    return scale_list


def setup(bot):
    Admin(bot)