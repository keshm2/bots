import discord
from discord.ext import commands
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import asyncio
import logs

load_dotenv()
token = os.getenv('TOKEN')
script_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_path, "discord.log")
handler = logging.FileHandler(filename=log_path, encoding='utf-8', mode='a+')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")



log = logs.Logger("bot")
client = commands.Bot(command_prefix='!', intents=intents, owner_id=536044633311019009)

@client.event
async def on_ready():
    local_time = datetime.now()
    local_time = local_time.strftime("%m-%d-%Y %H:%M:%S")
    print(f'{client.user.name} online at {local_time}')
    log.info(f'{client.user.name} online at {local_time}')

    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f'Talking sven'))


@client.command()
@commands.is_owner()
async def ping(ctx):
	msg = await ctx.send('Calculating ping...')
	await asyncio.sleep(2)
	await msg.edit(content = f'Bot ping is: `{round(client.latency * 1000)}` ms')
     
@client.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send('Bye bye 💔')
    log.info(f'Client shutdown by {ctx.author}')
    await client.close()


# ------- Error Handling ---------- #
@shutdown.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.NotOwner):
          await ctx.send('Erm, you don\'t own me 😳')
          log.info(f'{ctx.author} tried to shut me down :(')
    else:
         raise error

@ping.error
async def ping_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send('Erm, why do you want to know my ping 🤔')
        log.info(f'{ctx.author} tried to know my ping ??')
    else: 
        raise error
     


client.run(token=token, log_handler=handler, log_level=logging.INFO)