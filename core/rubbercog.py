import discord
from discord.ext import commands

import utils
from config.config import Config as config
from config.messages import Messages as messages

class RubberCog (commands.Cog):
    """Main cog class"""
    self.visible = True

    def __init__ (self, bot: commands.Bot, visible: bool = True):
        super().__init__(bot)
        self.bot = bot
        self.visible = visible

    ##
    ## Helper functions
    ##

    def _getEmbedTitle (self, ctx: commands.Context):
        """Helper function assembling title for embeds"""
        if ctx.command is None:
            return "(no command)"

        path = ' '.join((p.name) for p in ctx.command.parents) + \
               ' ' if ctx.command.parents else ''
        return config.prefix + path + ctx.command.name

    def _getEmbed (self, ctx: commands.Context, color: int = None, pin = False):
        """Helper function for creating embeds

        color: embed color
        pin: whether to pin the embed or let it be deleted
        """
        if color not in config.colors:
            color = config['base']
        if pin is not None and pin:
            title = "📌 " + self._getEmbedTitle(ctx)
        else:
            title = self._getEmbedTitle(ctx)
        description = "**{}**".format(ctx.command.cog_name) if ctx.command else ''

        embed = discord.Embed(title=title, description=description, color=color)
        if ctx.author is not None:
            embed.set_footer(ctx.author, icon_url=ctx.author.avatar_url)
        return embed

    async def deleteCommand(self, ctx: commands.Context, now: bool = True):
        """Try to delete the context message.

        now: Do not wait for message delay"""
        delay = 0.0 if now else config.delay_embed
        try:
            await ctx.message.delete(delay=delay)
        except discord.HTTPException:
            #TODO log
            pass

    def parseArg (self, arg: str = None):
        """Return true if supported argument is matched"""
        args = ["pin", "force"]
        return True if arg in args else False


    ##
    ## Embeds
    ##
    async def triggerError (self, ctx: commands.Context, errmsg: str,
                                  delete: bool = False, pin: bool = None):
        """Show an embed with thrown error."""
        embed = self._getEmbed(ctx, color=config.colors['error'], pin=pin)
        embed.add_field(name="Nastala chyba", value=errmsg, inline=False)
        embed.add_field(name="Příkaz", value=ctx.message.content, inline=False)
        delete = False if pin else delete
        if delete:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        else:
            await ctx.send(embed=embed)
        await self.deleteCommand(ctx, now=True)

    async def triggerNotify (self, ctx: commands.Context, msg: str,
                                   pin: bool = False):
        """Show an embed with a message."""
        embed = self._getEmbed(ctx, color=config.colors['notify'], pin=pin)
        embed.add_field(name="Upozornění", value=msg, inline=False)
        embed.add_field(name="Příkaz", value=ctx.message.content, inline=False)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)

    async def triggerDescription (self, ctx: commands.Context, pin: bool = False):
        """Show an embed with full docstring content."""
        #TODO Make first line and parameters bold
        embed = self._getEmbed(ctx)
        embed.add_field(name="O funkci", value=ctx.command.short_doc)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)
        
    async def triggerHelp (self, ctx: commands.Context, pin: bool = False):
        """Show an embed with help. Show options for groups"""
        embed = self._getEmbed(ctx)
        embed.add_field(name="Nápověda", value=ctx.command.help)

        if ctx.command.commands:
            for opt in sorted(ctx.command.commands):
                embed.add_field(name=opt.name, value=opt.short_doc, inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)