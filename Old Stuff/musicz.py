import discord  
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl
import os
from os import system
import shutil

queues = {}
client = commands.Bot(command_prefix = "/")

@client.event
async def on_ready():
    print("Ready.")

@client.command(pass_context = True)
async def join(ctx):
    if ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()

        await ctx.send(f"Joined `**{channel.name}**` and bound to `**{ctx.channel.name}**`!")
    else:
        await ctx.send(f":person_facepalming: You are not in any voice channel!")
@client.command(pass_context = True, aliases = ['dc','disconnect'])
async def leave(ctx):
    if ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        server = ctx.message.guild.voice_client
        await server.disconnect()
        await ctx.send(f"**Successfully disconnected from `{channel.name}`!** :thumbsup:")
        os.remove("song.mp3")
        shutil.rmtree("./Queue")
    else:
        await ctx.send(f"I am currently not in any channel!")


@client.command(pass_context=True, aliases=['p'])
async def play(ctx, *url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_g = length - 1
            try: 
                first_file = os.listdir(DIR)[0]
            except:
                print("No songs queued!")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next one queued\n")
                print(f"Songs still in queue: {still_g}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')
                voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda e: print("Music has finished!"))
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.volume = 0.25
            else:
                queues.clear()
                return

        else: 
            queues.clear()
            print("No songs were queued before the last one ended!\n")

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            await ctx.send (f"The song has been removed from the queue!")
    except PermissionError:
        await ctx.send (f":no_entry_sign: Error: Music still playing!")
        return
    except youtube_dl.utils.DownloadError: 
        await ctx.send (f":no_entry_sign: Something went wrong while downloading the video! Try again.")
    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_infile = "./Queue"
        if Queue_infle is True:
            print("Removed Old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old queue folder found!")
        



    await ctx.send(f":white_check_mark: Queued! Song to start playing soon!")
    voice = get(client.voice_clients, guild=ctx.guild)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet' : True,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    
    song_search = " ".join(url)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading the audio player now\n")
        ydl.download([f"ytsearch1:{song_search}"])

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.volume = 0.25

    
    

@client.command(pass_context  = True, aliases = ['pa'])
async def pause(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        await ctx.send(f":thumbsup: Music paused!")
    else:
        await ctx.send(f"Music not playing, how can you pause?")

@client.command(pass_context  = True, aliases = ['r'])
async def resume(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        await ctx.send(f":thumbsup: Resuming!")
    else:
        await ctx.send(f"Music not playing, how can you resume?")

@client.command(pass_context  = True, aliases = ['st','s'])
async def stop(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)
    queues.clear()
    if voice and voice.is_playing() or voice.is_paused():
        voice.stop()
        await ctx.send(f":thumbsup: Stopped and deleted the current music!")
        os.remove("song.mp3")
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            shutil.rmtree("./Queue")
    else:
        await ctx.send(f"Music not playing, how can you stop?")

@client.command(pass_context  = True, aliases = ['skip','n'])
async def next(ctx):
    
    if voice and voice.is_playing() or voice.is_paused():
        voice.stop()
        await ctx.send(f":thumbsup: Skipped the current music!")
        
    else:
        await ctx.send(f"Music not playing, how can you skip?")


@client.command(pass_context = True, aliases = ['q'])
async def queue(ctx, *url:str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else: 
            add_queue = False
            queues[q_num] = q_num
    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet' : True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url
        )
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading the audio player now\n")
        ydl.download(f"ytsearch1:{song_search}")
    await ctx.send(f":thumbsup: Song added! It is number " + str(q_num) + " in the queue :slight_smile:")

    


client.run("OTYxNDcyMzcwOTU3MjQ2NDg1.Yk5e7A.MRtCOXMIVErodivbQcTyIHp3xDM")