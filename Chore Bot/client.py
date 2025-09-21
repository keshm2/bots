import discord
from discord.ext import commands
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import asyncio
import logs
from logs import load_ids, update_ids
import aiohttp

# -------- Intial set up -------- #

load_dotenv()
token = os.getenv('TOKEN')
script_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_path, "discord.log")
id_path = os.path.join(script_path, "ids.json")
handler = logging.FileHandler(filename=log_path, encoding='utf-8', mode='a+')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
logging.basicConfig(level=logging.INFO,
					format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")



log = logs.Logger("bot")
list_id = load_ids(id_path, log)

print(id_path)
client = commands.Bot(command_prefix='!', intents=intents, owner_id=536044633311019009)

# -------- Owner commands ------- #

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

@client.command()
@commands.is_owner()
async def activity(ctx):
	activity_types = ['listening','watching','playing','streaming']
	try:
		await ctx.send('What do you want to change the activity to?')
		message = await client.wait_for('message', timeout = 5.0)
		if(message.content.lower() not in activity_types):
			return await ctx.send('That is not a valid activity type')
		if(message.content.lower() == 'listening'):
			await ctx.send("What is the client listening to?")
			msg = await client.wait_for('message', timeout = 10.0)
			await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{msg.content}"))
			await ctx.send(f"Client\'s status changed to: Listening to {msg.content}")
			return
		if(message.content.lower() == 'watching'):
			await ctx.send('What is the client watching?')
			msg = await client.wait_for('message', timeout = 10.0)
			await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f'{msg.content}'))
			await ctx.send(f'Client\'s status changed to: Watching {msg.content}')
			return
		if(message.content.lower() == 'playing'):
			await ctx.send('What is the client playing?')
			msg = await client.wait_for('message', timeout = 10.0)
			await client.change_presence(activity = discord.Game(name = f'{msg.content}'))
			await ctx.send(f'Client\'s status changed to: Playing {msg.content}')
			return
		if(message.content.lower() == 'streaming'):
			await ctx.send('What is the client streaming?')
			msg = await client.wait_for('message', timeout = 10.0)
			await client.change_presence(activity = discord.Streaming(name = f'{msg.content}', url = 'https://twitch.tv/Pika!'))
			await ctx.send(f'Client\'s status changed to: Streaming {msg.content}')
			return
	except asyncio.TimeoutError:
		msg = await ctx.send('Time ran out, try again')
		await asyncio.sleep(2)
		await msg.delete()
		

# --------- Generic commands --------- #
@client.command()
async def search(ctx, *, query: str = None):
	if query is not None:
		API_KEY = os.getenv("GOOGLE_API")
		SEARCH_ID = os.getenv("SEARCH_ENGINE_ID")

		url = "https://www.googleapis.com/customsearch/v1"
		params = {
			"key": API_KEY,
			"cx": SEARCH_ID,
			"q": query,
			"num": 5
		}

		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(url, params=params) as response:
					if response.status == 200:
						log.info(f'Search used by {ctx.author}')
						data = await response.json()
						embed = ""

						if 'items' not in data:
							embed = discord.Embed(title = f'Results for {query}',
							 description = 'No results found 🥀',
							 color = discord.Color.red())
						
						else:
							results = []
							for i, item in enumerate(data['items'][:5], 1):
								title = item.get('title', 'No title')
								link = item.get('link', '')
								results.append(f"**{i}. [{title}]({link})**")

								embed = discord.Embed(
									title = f"Results for {query}",
									description = "\n".join(results),
									color = 0x05e340
								)
						
						embed.set_footer(icon_url=ctx.author.display_avatar.url, text = f'Searched by {ctx.author.display_name}')
						await ctx.send(embed=embed)

					elif response.status != 200:
						embed = discord.Embed(title = f'Results for {query}',
							 description = 'No results found 🥀',
							 color = discord.Color.red())
						log.warning(f'Search for {query} returned with status {response.status}, searched by {ctx.author}')
						await ctx.send(embed = embed)

		except Exception as e:
			log.error(f'Searched failed with error: {str(e)}')


# --------------- Chore commands ---------------- #
@client.command()
async def add(ctx, *, list_name: str = None):
	await asyncio.sleep(0.2)
	try:
		await ctx.message.delete()
	
	except discord.Forbidden:
		await ctx.send(f"{ctx.author.mention} I have pee pee poo poo :( Enable server DMs so I can DM you 🥺")
	
	if list_name is None:
		await ctx.author.send(f"{ctx.author.mention}, uh oh, I no no get list name.\n**The list name is set to: List {list_id}**")
		list_name = f"List {list_id}"
		update_ids(id_path)
	
	else:
		await ctx.author.send(f"{ctx.author.mention}, new chore list created with list name: **{list_name}**")

	def dm_check(msg: discord.Message):
		return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)




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
	
@activity.error
async def activity_error(ctx, error):
	if isinstance(error, commands.NotOwner):
		await ctx.send("Pee pee poo poo check 🖐️")
		log.info(f'{ctx.author} tried to change what I was doing')
	else:
		raise error
	 


client.run(token=token, log_handler=handler, log_level=logging.INFO)