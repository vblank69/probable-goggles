import discord
from discord.ext import commands
from multimedia.playlist import Playlist
from helper_vars import *

class MultimediaManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guilds_playlists = {}
        for guild in bot.guilds:
            self.guilds_playlists[guild] = Playlist(bot)
        self.supported_sites = ['YouTube']
        self._playlist: Playlist = None
        self._author_vc: discord.VoiceState = None
        return None

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        response = discord.Embed(color=discord.Color.red())
        response.add_field(name='Error', value='{}'.format(str(error)), inline=False)
        await ctx.send(embed=response, ephemeral=True)
        return None

    async def cog_before_invoke(self, ctx: commands.Context):
        ##################################
        # Pre processing
        self._playlist: Playlist = self.guilds_playlists[ctx.guild]
        self._playlist.ctx_channel = ctx.channel
        self._playlist._bot_vc = ctx.voice_client
        self._author_vc = ctx.author.voice
        ##################################
        # Ensure the author is in a voice channel
        # and if the bot is in the same channel
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError(ERROR_NOT_IN_A_CHANNEL)
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError(ERROR_DIFFERENT_CHANNEL)
        return None

    @commands.hybrid_command(name='clear', aliases=['clr', 'cls'], help = COMMAND_CLEAR)
    async def _clear(self, ctx: commands.Context):
        # Clears the queue.
        response = self._playlist.clear()
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='disconnect', aliases=['dc', 'dd', 'leave'], help = COMMAND_DISCONNECT)
    async def _disconnect(self, ctx: commands.Context):
        # Clears the queue and disconnects from the channel.
        response = await self._playlist.disconnect()
        await ctx.send(embed=response, ephemeral=True)
        return None
    
    @commands.hybrid_command(name='download', aliases=['dl'])
    async def _download(self, ctx: commands.Context, link: str):
        # Clears the queue and disconnects from the channel.
        await ctx.defer()
        response = await self._playlist.download(link)
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='loop', aliases=['l', 'll'], help = COMMAND_LOOP)
    async def _loop(self, ctx: commands.Context):
        # Loop disabled, loop song, loop playlist.
        response = self._playlist.loop()
        await ctx.send(embed=response)
        return None
    
    @commands.hybrid_command(name='move', aliases=['mv'], help = COMMAND_MOVE)
    async def _move(self, ctx: commands.Context, position_now: int, position_new: int):
        # Print informations about the audio being reproduced.
        response = self._playlist.move(position_now, position_new)
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='now_playing', aliases=['now', 'np'], help = COMMAND_NOW_PLAYING)
    async def _now_playing(self, ctx: commands.Context):
        # Print informations about the audio being reproduced.
        response = self._playlist.now_playing
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='pause', help = COMMAND_PAUSE)
    async def _pause(self, ctx: commands.Context):
        # Pause
        response = self._playlist.pause()
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='play', aliases=['p', 'pl'], help = COMMAND_PLAY)
    async def _play(self, ctx: commands.Context, link=None):
        # If our client isnt connected to a channel already it will
        # try to connect to the authors channel and then will add the
        # music to the playlist, else it will print an error message.
        await ctx.defer()
        response = self._playlist.add(link)
        await self._playlist.play(self._author_vc)
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='playnext', aliases=['pn'], help = COMMAND_PLAY)
    async def _playnext(self, ctx: commands.Context, link: str):
        # If our client isnt connected to a channel already it will
        # try to connect to the authors channel and then will add the
        # music to the playlist, else it will print an error message.
        await ctx.defer()
        response = self._playlist.add(link)
        self._playlist.move(-1, 0)
        await self._playlist.play(self._author_vc)
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='queue', aliases=['q'], help = COMMAND_QUEUE)
    async def _queue(self, ctx: commands.Context):
        # Print the list of medias in the queue.
        response = self._playlist.queue()
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='remove', aliases=['r', 'rm'], help = '')
    async def _remove(self, ctx: commands.Context, index: int):
        response = self._playlist.remove(index)
        await ctx.send(embed=response)
        return None

    @commands.hybrid_command(name='skip', aliases=['s', 'sk', 'skp', 'next', 'n', 'nxt'], help = COMMAND_SKIP)
    async def _skip(self, ctx: commands.Context):
        # Stop playing the current audio and plays the next.
        embed = discord.Embed()
        embed.add_field(name="", value=":x: Skipping current song.")
        await ctx.send(embed=embed)
        response = await self._playlist.skip(True)
        if not response:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name="", value=":x: Nothing playing right now.")
            await ctx.message.edit(embed=embed)
        return None

    @commands.hybrid_command(name='stop', aliases=['stp', 'stap'], help = COMMAND_STOP)
    async def _stop(self, ctx: commands.Context):
        # Stop playing audio and clears the queue.
        response = self._playlist.stop()
        await ctx.send(embed=response)
        return None


async def setup(bot):
    await bot.add_cog(MultimediaManager(bot))
    return None
