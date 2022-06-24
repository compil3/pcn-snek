import logging
import os
import pathlib
from importlib import import_module
from inspect import getmembers, isclass
from os import curdir, listdir
from pkgutil import iter_modules
from types import ModuleType
from typing import Any, Dict

import extensions
from naff import (ComponentContext, Embed, Extension, InteractionContext, OptionTypes,
                  Permissions, Select, SelectOption, SlashCommand, check,
                  component_callback, errors, listen, slash_command,
                  slash_option, spread_to_rows)
from naff.client.utils.misc_utils import find_all
from naff.models.naff.extension import Extension
from naff.models.discord.components import ActionRow, Button, ButtonStyles
from naff.api.events import Component

format = "%b %d %Y %I:%M%p"
 
def get_commands():
    """Goes through extensions folder and returns a list of Extensions.
    Return class names and path.
    """
    commands = []
    command_path = ""
    for root, dirs, files in os.walk('extensions'):
        for file in files:
            if file.endswith(".py") and not file.startswith("__init__") and not file.startswith("__"):
                file = file.removesuffix(".py")
                path = os.path.join(root, file)
                command_path = path.replace("/", ".").replace("\\", ".")
                modname = import_module(command_path)
                for name, obj in getmembers(modname):
                    if isclass(obj) and issubclass(obj, Extension):
                        if obj.__name__ == "Extension":
                            continue
                        else:
                            commands.append((obj.__name__, command_path))
    return commands

   
class Update(Extension):

    @slash_command(
        "reloader",
        description="Reloads a scale.",
        scopes=[689119429375819951],
        default_member_permissions=Permissions.MANAGE_GUILD
    )
    async def _reloader(self, ctx: ComponentContext):
        await ctx.defer(ephemeral=True)
        commands = get_commands()
        command_buttons = []

        try:
            for command in commands:
               command_buttons.append(
                Button(
                    style=ButtonStyles.BLURPLE,
                    label=command[0],
                    custom_id=command[0],
                )
               )
            component: list[ActionRow] = spread_to_rows(*command_buttons)
            await ctx.send("Select Extension", components=component)                
        except Exception as e:
            print(e)

    @listen()
    async def on_component(self, event: Component):
        ctx = event.context
        await ctx.defer(edit_origin=True)
        embed = Embed(title="Extension Reloader", color=0x808080)
        command_list = get_commands()
        for command in command_list:
            if command[0] == ctx.custom_id:
                try:
                    self.bot.reload_extension(command[1])
                    embed.add_field("Reloaded Extension", value=f"**{ctx.custom_id}**", inline=False)
                    await ctx.edit_origin(embeds=[embed], components=[])
                    return
                except errors.ExtensionNotFound:
                    pass
                except errors.ExtensionLoadException:
                    await ctx.edit_origin(f"Failed to reload {ctx.custom_id}", components=[])

def setup(bot) -> None:
    Update(bot)
