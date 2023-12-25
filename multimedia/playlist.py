import discord
from discord.ext import commands
from .spotify import *
from .youtube import *

class Playlist():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.list_of_medias = []
        self._now_playing = None
        self._loop = 0
        self.ctx_channel: commands.Context
        self._bot_vc: discord.VoiceProtocol = None
        self._ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        return None
    
    @property
    def now_playing(self):
        # Print informations about the audio being reproduced.
        response = discord.Embed()
        if self._now_playing is None:
            response.color = discord.Color.red()
            response.add_field(name="", value=":x: Not playing anything right now.")
        else:
            response.title = "Now Playing"
            if self._bot_vc.is_paused():
                response.title = "Paused"
            response.add_field(name="", value=self._now_playing.title)
        return response
    
    @now_playing.setter
    def now_playing(self, media):
        self._now_playing = media
        return None

    def add(self, track: str = None):
        media_dict = Spotify.extract_info(track)
        if media_dict is None:
            media_dict = Audio.extract_info(track)
            self.list_of_medias.append(Audio(media_dict))
        else:
            if media_dict.get('type') == 'track':
                self.list_of_medias.append(Spotify(media_dict))
            else:
                for item in media_dict.get('tracks').get('items'):
                    self.list_of_medias.append(Spotify(item))
        response = discord.Embed(color=discord.Color.green())
        response.add_field(name='', value=f':white_check_mark: {media_dict["title"]} has been queued.')
        return response

    async def connect(self, author_vc: discord.VoiceState):
        # Try connecting to the same voice channel as the author.
        if self._bot_vc is None:
            await author_vc.channel.connect(timeout=5)
        elif not self._bot_vc.is_connected():
            await author_vc.channel.connect(timeout=5)
        elif self._bot_vc.channel != author_vc.channel:
            await self._bot_vc.move_to(author_vc.channel)
        response = discord.Embed()
        response.color = discord.Color.green()
        response.add_field(name="", value=":white_check_mark: Connected to your channel.")
        return response

    def clear(self):
        # Clears the queue.
        self.list_of_medias.clear()
        response = discord.Embed(color=discord.Color.green())
        response.add_field(name="", value=":white_check_mark: Queue cleared.")
        return response

    async def disconnect(self):
        # Clears the queue and disconnects from the channel.
        response = discord.Embed()
        if self._bot_vc is not None:
            self.list_of_medias.clear()
            self._bot_vc.stop()
            await self._bot_vc.disconnect()
            response.color = discord.Color.green()
            response.add_field(name="", value=":white_check_mark: Leaving voice channel.")
        else:
            response.color = discord.Color.red()
            response.add_field(name="", value=":x: I'm not connected to any channel.")
        return response
    
    async def download(self, link):
        response = discord.Embed()
        try:
            dl_url = Audio.extract_info(link)
            dl_url = dl_url['audio_loc']
            response.color = discord.Color.green()
            response.add_field(name='', value=f'[Your link is ready]({dl_url})')
        except:
            response.color = discord.Color.red()
            response.add_field(name='', value='I wasn\'t able to get a download link for that, sorry.')
        return response

    def loop(self):
        # Loop disabled, loop song, loop playlist.
        response = discord.Embed()
        self._loop = (self._loop+1) % 3
        if self._loop == 0:
            response.add_field(name="", value="Looping is set to None.")
        if self._loop == 1:
            response.add_field(name="", value="Looping is set to Song.")
        if self._loop == 2:
            response.add_field(name="", value="Looping is set to Playlist.")
        return response

    def move(self, position_now: int, position_new: int):
        to_move = self.list_of_medias.pop(position_now)
        self.list_of_medias.insert(position_new, to_move)
        response = discord.Embed()
        response.add_field(name='', value=f'Moved song \"{to_move.title} from position {position_now} to position {position_new}.')
        return response

    def pause(self):
        # If it's paused then we resume it,
        # if not, then we pause it.
        response = discord.Embed(color=discord.Color.red())
        if self._bot_vc is None:
            response.add_field(name="", value=":x: I am not in a channel right now.")
        else:
            response.color = discord.Color.green()
            if self._bot_vc.is_paused():
                self._bot_vc.resume()
                response.add_field(name="", value="Resumed playing.")
            elif self._bot_vc.is_playing():
                self._bot_vc.pause()
                response.add_field(name="", value="Paused.")
            else:
                self._bot_vc.pause()
                response.add_field(name="", value="I'm not playing anything right now.")
        return response

    def _play_next(self):
        self.bot.loop.create_task(self.skip(False))

    async def play(self, author_vc: discord.VoiceState):
        # If our client isnt connected to a channel already it will
        # try to connect to the authors channel and then will add the
        # music to the playlist, else it will print an error message.
        if(self._bot_vc is None):
            self._bot_vc = await author_vc.channel.connect()
        if not self._bot_vc.is_playing() and not self._bot_vc.is_paused():
            self._play_next()
        return None

    def queue(self):
        # Print the list of medias in the queue.
        response = discord.Embed(title="Queue")
        if len(self.list_of_medias) == 0:
            response.color = discord.Color.red()
            response.add_field(name="", value="There's nothing in the queue yet.")
        else:
            titles_list = ''
            for media in self.list_of_medias:
                titles_list += media.title + '\r'
            response.add_field(name="**Title**", value=titles_list, inline=False)
        return response
    
    def remove(self, index: int):
        response = discord.Embed()
        if (index < 1) or (index >= len(self.list_of_medias)):
            response.add_field(name='', value=':x: Index out of range!')
        else:
            removed = self.list_of_medias.pop(index)
            response.add_field(name='', value=f'{removed.title} was removed from the queue.')
        return response

    async def skip(self, skip: bool = False):
        # Stop playing the current audio and plays the next.
        response = True
        if skip:
            if self._now_playing is None:
                response = False
            else:
                if len(self.list_of_medias) == 0:
                    self._bot_vc.stop()
                else:
                    self.now_playing = self.list_of_medias.pop(0)
                    if self._loop == 2:
                        self.list_of_medias.append(self._now_playing)
                    self._bot_vc.source = discord.FFmpegOpusAudio(
                                            self._now_playing.get_source(),
                                            **self._ffmpeg_options)
                    await self.ctx_channel.send(embed=self.now_playing)
        else:
            if (self._loop != 1):
                if len(self.list_of_medias) > 0:
                    self.now_playing = self.list_of_medias.pop(0)
                else:
                    self.now_playing = None
            if self._loop == 2:
                self.list_of_medias.append(self._now_playing)
            if self._now_playing is not None:
                self._bot_vc.play(discord.FFmpegOpusAudio(source = self._now_playing.get_source(),
                                    **self._ffmpeg_options), after = lambda x: self._play_next())
            await self.ctx_channel.send(embed=self.now_playing)
        return response

    def stop(self):
        # Stop playing audio and clears the queue.
        self.list_of_medias.clear()
        self._bot_vc.stop()
        response = discord.Embed(color=discord.Color.green())
        response.add_field(name="", value="Playback has been stopped.")
        return response
