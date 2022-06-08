from naff import Context, Permissions


def user_has_player_role () -> bool:
    """Check if the user has the player role."""

    async def predicate(ctx: Context) -> bool:
        has_role =  ctx.author.has_role(ctx.guild.get_role(843899510483976233))
        return has_role

    return predicate
