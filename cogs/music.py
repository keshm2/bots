import discord
from discord.ext import commands
import asyncio
import pafy
import youtube_dl
from music import player
class Player(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.song_queue = {}
        self.setup()

    def setup(self):
        for guild in client.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)
    async def search_song(self, amount, song, get_url = False):
        info = await self.client.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format": "bestaudio", "quiet": True}).extract_info(f'ytsearch{amount}:{song}', download = False, ie_key = "YoutubeSearch"))
        if len(info['entries']) == 0: return None

        return [entry['webpage_url'] for entry in info['entries']] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after = lambda error:self.client.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = int(0.5)
    @commands.command()
    async def join(self, ctx):
        if ctx.message.author.voice is None:
            return await ctx.send(f'{ctx.author.mention}, you are not connected to any voice channel for me to join')
            

        if ctx.voice_client is not None:
            await ctx.send(f'{ctx.author.mention} I am already in a voice channel!')

        await ctx.author.voice.channel.connect()
        await ctx.send(f'Successfully joined the voice channel {channel.name}!')

    @commands.command(aliases = ['dc', 'disconnect'])
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
            await ctx.send('Successfully disconnected!')
        await ctx.send(f'{ctx.author.mention}, I am not connect to any of the voice channels.')
    @commands.command()
    async def play(self, ctx,*, song = None):
        if song is None:
            return await ctx.send(f'{ctx.author.mention}, please mention a song or video to play.')

        if ctx.voice_client is None:
            return await ctx.send(f'I am not in any channel to play this, {ctx.author.mention}.')
        if not('youtube.com/watch?' in song or 'https://youtu.be/' in song):
            await ctx.send('Searching for the requested song, this may take a few seconds.')
            result = await self.search_song(1, song, get_url = True)
            if result is None:
                return await ctx.send(f'{ctx.author.mention}, I could not find any song which matches those search terms')

            song = result[0]
        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])
            if queue_len < 20:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(f'{ctx.author.mention}, the requested song has been added to queue at position {queue_len+1}')

            else:
                return await ctx.send('The queue is at its max limit of 20, please wait for this song to finish to add more')


        await self.play_song(ctx,song)
        await ctx.send(f' Now playing: {song}')

    @commands.command()
    async def search(self, ctx, *, song = None):
        if song is None: return await ctx.send('You forgot to include a search term')

        await ctx.send('Searching for song, this may take a few seconds')

        info = await self.search_song(5, song)

        embed = discord.Embed(title = f"Results for '{song}':", description = 'You can use these URLs if the song requested is not the first result. *\n', color = 0x65FE08)
        amount = 0
        for entry in info['entries']:
            embed.description.append(f"[{entry['title']}]({entry['webpage_url']})\n")
            amount += 1

        embed.set_footer(text = f'Displaying the first {amount} results.')
        await ctx.send(embed = embed)
    @commands.command(aliases = ['q'])
    async def queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send('There are no songs in the current queue')

        embed = discord.Embed(title = 'Song Queue', description = '', color = 0x1F51FF)
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            embed.description += f'{i} {url} \n'

            i += 1

        embed.set_footer(text = f'Queue requested by: {ctx.author}')
        await ctx.send(embed = embed)
    @commands.command(aliases = ['next'])
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send('I am not playing any song, I cant skip an empty queue')

        if ctx.author.voice is None:
            return await ctx.send(f'{ctx.author.mention}, you are not connected to any voice channel')

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send(f'I am not in your voice channel, {ctx.author.mention}.')
        poll = discord.Embed(f'Vote to skip the current song! Vote started by - {ctx.author.mention}', description = f'**80% of the members in the voice channel {channel.name} must agree to skip**')
        poll.add_field(name = 'Skip', value = ':white_check_mark:')
        poll.add_field(name = 'Stay', value = ':x:')
        poll.set_footer(text = 'Voting ends in 10 seconds')

        poll_msg = await ctx.send(embed = poll)
        poll_id = poll_msg.id

        await poll_msg.add_reaction(u"\u2705")
        await poll_msg.add_reaction(u"\U0001F6AB")

        await asyncio.sleep(10)

        poll_msg = await ctx.channel.fetch_message(poll_id)

        votes = {u'\u2705' : 0, u'\U0001F6AB' : 0}
        reacted = []

        for reaction in poll_msg.reactions:
            if reaction.emoji in [u'\u2705', u'\U0001F6AB']:
                async for user in reaction.users():
                    if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                        votes[reaction.emoji] += 1

                        reacted.append(user.id)
        skip = False

        if votes[u'\u2705'] > 0:
            if votes[u'\U0001F6AB'] == 0 or votes[u'\u2705']/(votes[u'\u2705'] + votes[u'\U0001F6AB']) > 0.79:
                skip = True
                embed = discord.Embed(title = 'Skip sucessful!', description = '***Voting to skip the current song was sucessful!***', color = 0xFF69B4)

        if not skip:
            embed = discord.Embed(title = 'Skip failed', description = '*Voting to skip the current song has failed.*\n\n **Voting failed, the vote required more than 80 percent of the the members in the channel to agree.**')

        embed.set_footer(text = 'Voting has ended.')

        await poll_msg.clear_reactions()
        await poll_msg.edit(embed = embed)

        if skip:
            ctx.voice_client.stop()
            await self.check_queue(ctx)
