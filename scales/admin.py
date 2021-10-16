from os import listdir

from dis_snek.models.application_commands import Permission, slash_command, slash_permission
from dis_snek.models import ( Scale, Embed, scale)

import logging
import sys

guild_id = 689119429375819951
admin_perm = [Permission(842505724458172467, 1, True)]
class Admin(Scale):
    # FIXME: fix reload command
    @slash_command("reload", description="Reload all Scales", scope=guild_id)
    @slash_permission(guild_id=guild_id, permissions=admin_perm)
    async def reload(ctx):
        embed = Embed(title="Reloading all Scales!", color=0x808080)

        for filename in listdir("./scales"):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    scale.bot.regrow_scale(f"scales.{filename[:-3]}")
                    print(f"Loaded scales.{filename[:-3]}")
                    logging.info(f"scales.{filename[:-3]} loaded.")
                except Exception as e:
                    print(f"Failed to load scale {filename[:-3]}.", file=sys.stderr)

    #TODO: add a reload single scale command
def setup(bot):
    Admin(bot)