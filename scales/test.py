from dis_snek.models.scale import Scale 
from dis_snek.models import (Permission, slash_command, PermissionTypes)


class Test(Scale):

    @slash_command(
        "test_four",
        "just a test",
        scopes=[174342051318464512],
        default_permission=False,
        permissions=[
            Permission(176538785511768064, 174342051318464512, PermissionTypes.ROLE, True),
        ],
        )
    async def this_test(ctx):
        await ctx.send("you're permitted")

def setup(bot):
    Test(bot)



#  Won't work, greyed out
# thats amazing how it wont work for you
# what Intents are you using (won't matter much anyways) default
# trying on another server, hold on 
#LOL, i am pretty sure you are ratelimited

#  ffs it worked
# it's not showing at all that it is.
# set logging level to DEBUG and then search in the log for `Has exceeded ratelimit!`
# where am i setting it?... what logging level
# lol, I have a feeling this is a Discord server issue.

