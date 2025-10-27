import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

import logging
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from dotenv import load_dotenv
import os
import asyncio

import logs
from logs import save_chores, load_chores, load_ids, update_ids
import canvas_utils
from canvas_utils import users as _users
import chore_utils

import aiohttp
import requests
import re


import random
from utils import random_hex
from utils import EmbedPaginator 
from utils import poll_ics_once
import db_manager



# -------- Intial set up -------- #

load_dotenv()
token = os.getenv('TOKEN')
ical_link = os.getenv('ICS_LINK')
script_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_path, "discord.log")
image_links = ["https://www.meme-arsenal.com/memes/e01ffed4ee9ab49e216bc5bc7c38cde5.jpg", "https://pbs.twimg.com/media/Ei8NgNqXsAAGPtU?format=jpg&name=medium", "https://cdn11.bigcommerce.com/s-ydriczk/images/stencil/1500x1500/products/88251/90865/Prison-Minion-with-Bananas-cardboard-cutout-buy-now-at-Starsills__48033.1497885770.jpg?c=2"]
id_path = os.path.join(script_path, "ids.json")
chores_path = os.path.join(script_path, "chores.json")
DEV_GUILD = 818661605574574080


handler = logging.FileHandler(filename=log_path, encoding='utf-8', mode='a+')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
logging.basicConfig(level=logging.INFO,
					format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")



log = logs.Logger("bot")

client = commands.Bot(command_prefix='!', intents=intents, owner_id=536044633311019009)



# -------- Owner commands ------- #


@client.event
async def on_ready():
	local_time = datetime.now()
	local_time = local_time.strftime("%m-%d-%Y %H:%M:%S")

	try: 
		db_manager.init_all_databases()
	except Exception as e:
		log.critical(f'Database initialization failed: {str(e)}')
		print(f'❌ Database error: {str(e)}')
		await client.close()
		return
	
	try:
		guild = discord.Object(id = DEV_GUILD)
		client.tree.copy_global_to(guild = guild)
		await client.tree.sync(guild = guild)
	except Exception as e:
		log.critical(f'Failed to sync slash commands {str(e)}')
		print('Failed to sync commands')
	print(f'{client.user.name} online at {local_time}')
	log.info(f'{client.user.name} online at {local_time}')


	await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f'Talking sven'))
	poll_ics.start()
	poll_chores.start()

@client.command()
@commands.is_owner()
async def ping(ctx):
	msg = await ctx.send('Calculating ping...')
	await asyncio.sleep(2)
	await msg.edit(content = f'Bot ping is: `{round(client.latency * 1000)}` ms')
	return

@client.command()
@commands.is_owner()
async def backup(ctx):
	try:
		db_manager.backup_all_databases()
		await ctx.author.send('Backup created successfully')
	
	except Exception as e:
		await ctx.author.send(f'Backup failed: {str(e)}')
		log.error(f'Backup failed of databases:\n{str(e)}')
	return

	 
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


	
# --------------- Chore commands (JSON)---------------- #

'''
@client.command(aliases=['add', 'list'])
async def newlist(ctx, *, list_name: str = None):
	await asyncio.sleep(0.2)

	# load existing data
	chores = load_chores(file_path=chores_path) or {}
	user_key = str(ctx.author.id)
	chores.setdefault(user_key, {})  # user -> dict of lists

	try:
		await ctx.message.delete()
	except discord.Forbidden:
		return await ctx.send(f"{ctx.author.mention} I have pee pee poo poo :( Enable server DMs so I can DM you 🥺")

	if not list_name:
		list_id = load_ids(file_path=id_path, log=log)
		if list_id is None or list_id < 0:
			base, n = "List", 1
			existing = set(chores[user_key].keys())
			while f"{base} {n}" in existing:
				n += 1
			list_name = f"{base} {n}"
		else:
			list_name = f"List {list_id}"
			update_ids(file_path=id_path)

		await ctx.author.send(
			f"{ctx.author.mention}, uh oh, no list name.\n**The list name is set to: {list_name}**"
		)
	else:
		await ctx.author.send(f"{ctx.author.mention}, new chore list created: **{list_name}**")

	chores[user_key].setdefault(list_name, [])

	def dm_check(m: discord.Message):
		return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

	await ctx.author.send('Add chores below, type **done** when finished.')
	await ctx.author.send('Add each chore individually (I pee pee poo poo otherwise :( ))')

	num = 0
	while True:
		try:
			msg = await client.wait_for('message', check=dm_check, timeout=90.0)
		except asyncio.TimeoutError:
			await ctx.author.send("PEE PEE POO POO CHECK 😳, you timed out")
			break

		content = msg.content.strip()
		if content.lower() == "done":
			await ctx.author.send(
				f"Chores saved to **{list_name}**. To view the list, run `showlist {list_name}`"
			)
			await ctx.author.send(f'There were {num} chores added... wow....')
			break

		chores[user_key][list_name].append(content)
		num += 1
		await ctx.author.send(f"Added `{content}` to **{list_name}**. More? 😡")

	save_chores(data=chores, file_path=chores_path, append=False)
	return
'''


'''
@client.tree.command(name = 'newlist', description = 'Make a new chorelist for roomies 🥹')
@app_commands.describe(list_name = 'The chore list name')
async def newlist(interaction: discord.Interaction, list_name: str = None):
	await interaction.response.defer(ephemeral = True)
	
	chores = load_chores(file_path = chores_path) or {}
	uid = str(interaction.user.id)
	chores.setdefault(uid, {})

	if list_name in chores[uid]:
		await interaction.followup.send(f'Nuh uh, the list **{list_name}** was already created', ephemeral = True)
		return
	
	chores[uid][list_name] = {
		'server_id': interaction.guild.id if interaction.guild else None,
		'server_name': interaction.guild.name if interaction.guild else None,
		'chores': []
	}

	await interaction.followup.send(f'{interaction.user.mention}, new chore list created: **{list_name}**', ephemeral = True)
	await interaction.followup.send('Add chores below, type **done** when finished.', ephemeral = True)
	await interaction.followup.send('Add each chore individually (I pee pee poo poo otherwise :( ))', ephemeral = True)

	def check(msg: discord.Message):
		return msg.author == interaction.user and msg.channel == interaction.channel
	

	num = 0
	while True:
		try:
			msg = await client.wait_for("message", check = check, timeout = 60.0)
		
		except asyncio.TimeoutError:
			await interaction.followup.send("PEE PEE POO POO CHECK 😳, you timed out", ephemeral = True)
			await interaction.followup.send("Saving current chores", ephemeral = True)
			break

		chore = msg.content.strip()
		if chore.lower() == 'done':
			await interaction.followup.send(f"Chores saved to **{list_name}**. To view the list, run `showlist {list_name}`", ephemeral = True)
			await interaction.followup.send(f'There was {num} chore{"s" if num != 1 else ""} added... wow....', ephemeral = True)
			break

		await interaction.followup.send()
'''

@client.tree.command(name = 'newlist', description = 'Make a new chorelist for roomies 🥹')
@app_commands.describe(list_name = 'Name for the chore list')
async def newlist(interaction: discord.Interaction, list_name: str):
	await interaction.response.defer(ephemeral = True)

	uid = interaction.user.id


	if db_manager.get_list_by_name(uid, list_name):
		await interaction.followup.send(f'Nuh uh, the list **{list_name}** was already created', ephemeral = True)
		await interaction.followup.send(f'Run `/showlist with test as the list name to view the chore list', ephemeral = True)
		return
	
	list_id = db_manager.create_chore_list(uid, list_name, interaction.guild.id if interaction.guild else None)

	if not list_name:
		await interaction.followup.send(f"{interaction.user.mention}, uh oh, no list name.\n**The list name is set to: {list_name}**")
	
	await interaction.followup.send('Add chores below, type **done** when finished. Timeout is 90 seconds between messages', ephemeral = True)
	await interaction.followup.send('For each chore, necesito:\n1️⃣ The chore name\n2️⃣ When it should be done\n3️⃣ Who should do it', ephemeral = True)
	await interaction.followup.send('Add each chore individually (I pee pee poo poo otherwise :( ))', ephemeral = True)

	def check(msg: discord.Message):
		return msg.author == interaction.user and msg.channel == interaction.channel
	
	num = 0
	while True:
		await interaction.followup.send(f"\n**Chore #{num + 1}** - 😡 What's the chore? 😡 (or type **done** to finish) 😡", ephemeral = True)
		try:
			msg = await client.wait_for('message', check = check, timeout = 90.0)
		except asyncio.TimeoutError:
			await interaction.followup.send("PEE PEE POO POO CHECK 😳, you timed out", ephemeral = True)
			await interaction.followup.send("Saving current chores", ephemeral = True)
			break

		chore_name = msg.content.strip()
		if chore_name.lower() == 'done':
			await interaction.followup.send(
				f"Chores saved to **{list_name}**😱\n"
				f"Use `/showlist list_name:{list_name}` to view it", ephemeral = True
			)
			await interaction.followup.send(f'There was {num} chore{"s" if num != 1 else ""} added... wow....', ephemeral = True)
			break

		await interaction.followup.send(
			f"When should **{chore_name}** be done?\n"
			"• Recurring: `1 week`, `2 weeks`, `5 days`\n"
			"• Specific date: `10/16`, `12/25`, `oct 16`", ephemeral = True
		)

		frequency_result = 0
		attempts = 0

		while not frequency_result and attempts < 3:
			try:
				freq_msg = await client.wait_for('message', check= check, timeout=90.0)
			except asyncio.TimeoutError:
				await interaction.followup.send("PEE PEE POO POO CHECK 😳, you timed out", ephemeral = True)
				break
			
			frequency_result = chore_utils.parse_frequency(freq_msg.content)
			if not frequency_result:
				attempts += 1
				await interaction.followup.send("❌ Invalid format. Try again 😡", ephemeral = True)
		
		if not frequency_result:
			continue
		
		# Get assigned user
		await interaction.followup.send(
			f"Who should do **{chore_name}**?\n"
			"Mention them with @username or type their user ID", ephemeral = True
		)
		
		assigned_user_id = None
		attempts = 0
		while not assigned_user_id and attempts < 3:
			try:
				user_msg = await client.wait_for('message', check = check, timeout=90.0)
			except asyncio.TimeoutError:
				await interaction.followup.send("PEE PEE POO POO CHECK 😳, you timed out", ephemeral = True)
				break
			
			if user_msg.mentions:
				assigned_user_id = user_msg.mentions[0].id
			else:
				try:
					assigned_user_id = int(user_msg.content.strip())
				except ValueError:
					attempts += 1
					await interaction.followup.send("☹️ Couldn't find that user.", ephemeral = True)
					continue
			
			try:
				user = await client.fetch_user(assigned_user_id)
				await interaction.followup.send(f"✅ Chore assigned to **{user.name}** 😭", ephemeral = True)
			except discord.NotFound:
				assigned_user_id = None
				attempts += 1
				await interaction.followup.send("❌ User not found 😭✌️", ephemeral = True)
		
		if not assigned_user_id:
			continue
		
		now = datetime.now(canvas_utils.TZ)
		
		if frequency_result['type'] == 'one_time':
			db_manager.add_chore(
				list_id=list_id,
				name=chore_name,
				assigned_to=assigned_user_id,
				chore_type='one_time',
				due_date=frequency_result['date']
			)
			freq_display = frequency_result['date'].strftime("%B %d, %Y")
		else:
			db_manager.add_chore(
				list_id=list_id,
				name=chore_name,
				assigned_to=assigned_user_id,
				chore_type='recurring',
				frequency_days=frequency_result['days'],
				next_due=now
			)
			freq_display = f"every {frequency_result['days']} day{'s' if frequency_result['days'] != 1 else ''}"
		
		num += 1
		await interaction.followup.send(
			f"✅ Added **{chore_name}** ({freq_display}, assigned to <@{assigned_user_id}>)", ephemeral = True
		)




		
@client.tree.command(name = 'link_ics', description = 'Link your canvas calendar feed (.ics) for Discord reminders 📝')
@app_commands.describe(ics_link = 'Paste the link from Canvas here 🌹')
async def link_ics(interaction: discord.Interaction, ics_link: str):
	await interaction.response.defer(ephemeral = True)
	if not (ics_link.startswith('http://') or ics_link.startswith('https://')) or '.ics' and 'user' not in ics_link:
		await interaction.followup.send("That is NOT a calendar link...😡", ephemeral = True)
		await asyncio.sleep(3)
		await interaction.followup.send("A link looks like this: https://<link>.ics", ephemeral = True)
		return
	
	db_manager.set_user_ics(interaction.user.id, ics_link)

	await interaction.followup.send('HOORAY your calendar has been saved 🤓☝️', ephemeral = True)
	await asyncio.sleep(2)

	try:
		await interaction.user.send(f'{interaction.user.mention}, I will annoy you a day before any assignment is due :3')
		await interaction.user.send('Have a nice day 🤑')

	except discord.Forbidden:
		await interaction.followup.send("The bluetooth device didn't pair 💔 I can't DM you about assignments", ephemeral = True)
		return
	


	
@client.tree.command(name = 'assignments', description = 'List the next upcoming assignments')
@app_commands.describe(limit = 'Number of assignments to show, defaults to 1. All assignments can be seen with the word \'all\'')
async def assignments(interaction: discord.Interaction, limit: str = '1'):
	await interaction.response.defer(ephemeral = True)
	uid = interaction.user.id
	ics = db_manager.get_user_ics(uid)

	if not ics:
		await interaction.followup.send("Your calendar is empty 🤯... just kidding I don't have your ics link on file 🥺", ephemeral = True)
		await interaction.followup.send("Set your calendar link by grabbing the Canvas calendar link and using `!link_ics <link>` :3", ephemeral = True)
		return
	
	localtz = canvas_utils.tz_for_user(interaction.user.id)
	now = datetime.now(localtz)
	end = now + timedelta(days=120)

	try:
		r = requests.get(ics, timeout=30)
		r.raise_for_status()
		cal = canvas_utils.parse_ics(r.content)

	except Exception as e:
		log.error(f"Error fetching {interaction.user}'s ics link: {str(e)}")
		await interaction.followup.send("Uh oh I peed my pants :(, I couldn't get your calendar", ephemeral = True)
		return
	
	items = []
	for comp in cal.walk():
		if getattr(comp, 'name', None) != 'VEVENT':
			continue

		start = canvas_utils.event_start(comp=comp, localtz=localtz)
		if not start or start < now or start > end:
			continue

		title = str(comp.get('SUMMARY') or 'No summary given').strip()
		url = canvas_utils.event_url(comp=comp)
		desc = canvas_utils.event_description(comp=comp)
		if not canvas_utils.looks_like_assignment(title, desc, url):
			continue

		items.append((start, title, url))

	items.sort(key=lambda x: x[0])

	if isinstance(limit, str) and limit.lower() == "all":
		num = len(items)
	else:
		try:
			count = int(limit)
		except (TypeError, ValueError):
			count = 5
		num = max(1, min(count, 15))

	items = items[:num]
	
	if not items:
		await interaction.followup.send("It looks like you're all caught up 😳, your calendar was empty af", ephemeral = True)
		return
	
	total = len(items)

	def render_assignment(embed: discord.Embed, item: dict):
		when, title, url = item
		when_str = when.strftime("%a %b %d, %I:%M %p %Z")
		link = canvas_utils.build_url(url) or url or ""
		val = f"⏰ Due {when_str}"
		if link:
			val += f"\n🔗{link}"
		embed.add_field(name = title, value = val, inline = False)

	def page_desc(page_num: int, total_pages: int, start_idx: int, end_idx: int) -> str:
		return f"Page {page_num}/{total_pages} — showing {start_idx}-{end_idx} of **{total}**"
	
	embed = EmbedPaginator(
		items = items,
		author_id = interaction.user.id,
		per_page = 10,
		color = random_hex(),
		embed_title = f"**Next upcoming {total} {"assignment" if total < 2 else "assignments"} for {interaction.user.display_name}**",
		page_desc = page_desc,
		render_item = render_assignment,
		thumb_url = image_links[random.randint(0, 2)],
		timeout = 180.0
	)

	await interaction.followup.send(embed = embed._make_embed(), view = embed)


@client.tree.command(name = 'showlist', description = 'List ongoing chore list(s) and their chores')
@app_commands.describe(list_name = 'Name of the chore list to view, leave blank to see all active lists')
async def showlist(interaction: discord.Interaction, list_name: str = None):
	await interaction.response.defer(ephemeral = True)

	uid = interaction.user.id

	all_lists = db_manager.get_user_lists(uid)

	if not all_lists:
		await interaction.followup.send('No chore list found :(, make one with `/createlist`', ephemeral = True)
		return
	
	if not list_name:
		embed = discord.Embed(
			title = 'Shinglespag chore lists 😱',
			description = 'To view a specific list, use `/showlist <list_name>`',
			color = random_hex()
		)

		for chore_list in all_lists:
			status_parts = []

			chores = db_manager.get_list_chores(chore_list['id'])

			if chores:
				now = datetime.now(canvas_utils.TZ)
				overdue = 0
				due_soon = 0
				completed = 0

				for chore in chores:
					if chore['chore_type'] == 'one_time':
						if chore['completed']:
							completed += 1
							continue
						due_date = datetime.fromisoformat(chore['due_date'])
						if due_date < now:
							overdue += 1
						elif (due_date - now).days < 1:
							due_soon += 1
					else:
						if chore['last_completed']:
							last = datetime.fromisoformat(chore['last_completed'])
							next_due = last + timedelta(days=chore['frequency_days'])
						else:
							next_due = datetime.fromisoformat(chore['next_due'])
						
						if next_due < now:
							overdue += 1
						elif (next_due - now).days < 1:
							due_soon += 1
				
				if overdue > 0:
					status_parts.append(f" 🔴 {overdue} overdue")
				if due_soon > 0:
					status_parts.append(f" 🟡 {due_soon} due soon")
				if completed > 0:
					status_parts.append(f" ✅ {completed} completed")
				
				status = " • ".join(status_parts) if status_parts else "🟢 All on track"
			else:
				status = "Empty list"
			
			embed.add_field(
				name=f"📋 {chore_list['list_name']}",
				value=f"{chore_list['chore_count']} chore{'s' if chore_list['chore_count'] != 1 else ''} • {status}",
				inline=False
			)
		
		embed.set_footer(text="Tip: Use /showlist list_name:<name> to view a specific list")
		await interaction.followup.send(embed=embed, ephemeral=True)
		return
	
	chore_list = db_manager.get_list_by_name(uid, list_name)
	
	if not chore_list:
		available = ', '.join([l['list_name'] for l in all_lists])
		await interaction.followup.send(
			f"❌ List **{list_name}** not found.\nYour lists: {available}",
			ephemeral=True
		)
		return
	
	# Get chores from SQLite
	chores = db_manager.get_list_chores(chore_list['id'])
	
	if not chores:
		await interaction.followup.send(f"List **{list_name}** is empty!", ephemeral=True)
		return
	
	embed = discord.Embed(
		title=f"📋 {list_name}",
		description=f"Total chores: {len(chores)}",
		color=random_hex()
	)
	
	now = datetime.now(canvas_utils.TZ)
	
	for idx, chore in enumerate(chores, 1):
		try:
			assigned_user = await client.fetch_user(chore['assigned_to'])
			user_mention = assigned_user.mention
		except discord.NotFound:
			user_mention = f"<@{chore['assigned_to']}>"
		
		if chore['chore_type'] == 'one_time':
			due_date = datetime.fromisoformat(chore['due_date'])
			is_completed = bool(chore['completed'])
			
			if is_completed:
				status = " ✅ Completed"
			else:
				time_diff = due_date - now
				if time_diff.total_seconds() < 0:
					status = " 🔴 OVERDUE"
				elif time_diff.days < 1:
					status = " 🟡 Due soon"
				else:
					status = " 🟢 Upcoming"
			
			due_str = due_date.strftime("%b %d, %Y")
			embed.add_field(
				name=f"{idx}. {chore['name']} (One-time)",
				value=f"**Assigned to:** {user_mention}\n**Due:** {due_str} {status}",
				inline=False
			)
		else:
			if chore['last_completed']:
				last = datetime.fromisoformat(chore['last_completed'])
				next_due = last + timedelta(days=chore['frequency_days'])
			else:
				next_due = datetime.fromisoformat(chore['next_due'])
			
			time_diff = next_due - now
			if time_diff.total_seconds() < 0:
				status = " 🔴 OVERDUE"
			elif time_diff.days < 1:
				status = " 🟡 Due soon"
			else:
				status = " 🟢 On track"
			
			freq_str = f"every {chore['frequency_days']} day{'s' if chore['frequency_days'] != 1 else ''}"
			due_str = next_due.strftime("%b %d, %Y")
			
			embed.add_field(
				name=f"{idx}. {chore['name']}",
				value=f"**Assigned to:** {user_mention}\n**Frequency:** {freq_str}\n**Next due:** {due_str} {status}",
				inline=False
			)
	
	embed.set_footer(text="Use /complete to mark a chore as done")
	await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name = 'overdue', description = 'List overdue/completed assignments twin 🥹✌️')
@app_commands.describe(limit = "Number of overdue or completed assignments to show, default is 10")
async def overdue(interaction: discord.Interaction, limit: str = "10"):
	await interaction.response.defer(ephemeral=True)

	uid = interaction.user.id
	ics = canvas_utils.get_user_ics(uid)

	if not ics:
		await interaction.followup.send('Idk what your calendar looks like twin 🥀', ephemeral=True)
		await asyncio.sleep(2)
		await interaction.followup.send('Do `/link_ics` with your canvas calendar link', ephemeral=True)
		return
	
	localtz = canvas_utils.tz_for_user(uid=uid)
	now = datetime.now(localtz)

	try:
		r = requests.get(ics, timeout=30)
		r.raise_for_status()
		cal = canvas_utils.parse_ics(r.content)
	except Exception as e:
		await interaction.followup.send('Twin I blew up 💔 something went wrong', ephemeral=True)
		log.error(f'Error fetching {interaction.user}\'s calendar: {str(e)}')
		return
	
	try:
		overdue = []
		for comp in cal.walk():
			if getattr(comp, 'name', None) != "VEVENT":
				continue
		
			start = canvas_utils.event_start(comp=comp, localtz=localtz)
			if not start or start >= now:
				continue

			title = str(comp.get('SUMMARY') or 'No summary found').strip()
			url = canvas_utils.event_url(comp=comp)
			desc = canvas_utils.event_description(comp=comp)

			if not canvas_utils.looks_like_assignment(title, desc, url):
				continue

			time_diff = now - start
			days_overdue = time_diff.days
			hours_overdue = time_diff.seconds // 3600

			overdue.append({
				'title': title, 
				'due': start, 
				'url': url, 
				'days': days_overdue,
				'hours': hours_overdue
			})

		if not overdue:
			await interaction.followup.send('Goat you have zero assignments overdue 😱', ephemeral=True)
			return
		
		overdue.sort(key = lambda x: x['due'])

		if isinstance(limit, str) and limit.lower() == 'all':
			num = len(overdue)
		else:
			try:
				num = max(1, int(limit))
			except (TypeError, ValueError):
				num = 10

		overdue = overdue[:num]


		for item in overdue:
			item['link'] = canvas_utils.build_url(item['url']) or item['url']

		def render_overdue(embed: discord.Embed, item: dict):
			if item['days'] > 0:
				ago = f"{item['days']} day{'s' if item['days'] != 1 else ''} ago"
			elif item["hours"] > 0:
				ago = f"{item['hours']} hour{'s' if item['hours'] != 1 else ''} ago"
			else:
				ago = "Less than an hour ago"
			due_str = item["due"].strftime("%a %b %d, %I:%M %p %Z")
			val = f"**Due:** {due_str}\n**Overdue by:** {ago}"
			if item.get("link"):
				val += f"\n🔗 {item['link']}"
			embed.add_field(name=f"🍂 {item['title']}", value=val, inline=False)

		total = len(overdue)

		def page_desc(page_num: int, total_pages: int, start_idx: int, end_idx: int) -> str:
			return f"Page {page_num}/{total_pages} — showing {start_idx}-{end_idx} of **{total}**"
		
		embed = EmbedPaginator(
			items=overdue,
			author_id=interaction.user.id,
			per_page=10,
			color=random_hex(),
			embed_title="😡 **Overdue assignments**",
			page_desc=page_desc, 
			render_item=render_overdue,
			thumb_url=image_links[random.randint(0, 2)],
			footer_text=None,
			timeout=120.0
		)

		await interaction.followup.send(embed = embed._make_embed(), view = embed, ephemeral= True)
	
	except Exception as e:
		log.error(f"Error when {interaction.user} used the overdue command: {str(e)}")
		await interaction.followup.send('Twin I blew up 💔🥀 something went wrong', ephemeral=True)
		return



# ------ Looping tasks --------- #
@tasks.loop(minutes=canvas_utils.POLL_MIN)
async def poll_ics():
	users_with_ics = db_manager.get_all_users_with_ics()
	
	for user_data in users_with_ics:
		uid = user_data['user_id']
		ics_url = user_data['ics_link']
		
		localtz = canvas_utils.tz_for_user(uid=uid)
		now = datetime.now(localtz)
		end = now + timedelta(days=canvas_utils.LOOKAHEAD_DAYS)
		
		try:
			r = requests.get(ics_url, timeout=30)
			r.raise_for_status()
			cal = canvas_utils.parse_ics(r.content)
		except Exception as e:
			log.error(f'[{uid}] ICS fetch error: {e}')
			continue
		
		for comp in cal.walk():
			if getattr(comp, "name", None) != 'VEVENT':
				continue
			
			start = canvas_utils.event_start(comp=comp, localtz=localtz)
			if not start or start <= now or start > end:
				continue
			
			title = str(comp.get('SUMMARY') or "No summary given").strip()
			url = canvas_utils.event_url(comp=comp)
			desc = canvas_utils.event_description(comp=comp)
			
			if not canvas_utils.looks_like_assignment(title, desc, url):
				continue
			
			start_iso = start.isoformat()
			event_id = canvas_utils.event_uid(comp=comp, start_iso=start_iso)
			fp = canvas_utils.event_fingerprint(comp=comp, localtz=localtz)
			
			old_fp = db_manager.get_assignment_fingerprint(uid, event_id)
			
			if old_fp and old_fp != fp:
				when_str = start.strftime("%a %b %d, %I:%M %p %Z")
				link = canvas_utils.build_url(url) or url or ""
				
				short_desc = None
				if desc:
					short_desc = desc[:1000].rstrip() + "..." if len(desc) > 1000 else desc
				
				embed = discord.Embed(
					title=f"⏰ Due date updated: {title}"[:256], 
					description="This assignment's details changed 🤯",
					color=random_hex()
				)
				embed.add_field(name="New due time", value=when_str, inline=False)
				if link:
					embed.add_field(name="Link 🔗", value=f"{link}"[:1024], inline=False)
				if short_desc:
					embed.add_field(name="📝 Summary", value=short_desc, inline=False)
				embed.set_thumbnail(url=image_links[random.randint(0, 2)])
				
				try:
					user = await client.fetch_user(uid)
					await user.send(embed=embed)
				except discord.Forbidden:
					log.error(f'Could not DM user {uid}')
				
				db_manager.mark_assignment_reminder_sent(uid, event_id, 'update', fp)

			time_until_due = start - now
			hours_until_due = time_until_due.total_seconds() / 3600
			
			reminder_threshold = None
			if 24 >= hours_until_due > 12:
				reminder_threshold = '24h'
			elif 12 >= hours_until_due > 6:
				reminder_threshold = '12h'
			elif 6 >= hours_until_due > 3:
				reminder_threshold = '6h'
			elif 3 >= hours_until_due > 0:
				reminder_threshold = '3h'
			
			if reminder_threshold and not db_manager.check_assignment_reminder_sent(uid, event_id, reminder_threshold):
				when_str = start.strftime("%a %b %d, %I:%M %p %Z")
				link = canvas_utils.build_url(url) or url or ""
				
				short_desc = None
				if desc:
					short_desc = desc[:1000].rstrip() + "..." if len(desc) > 1000 else desc
				
				time_messages = {
					'24h': ("🍂", "is due in ~24 hours", random_hex()),
					'12h': ("⚠️", "is due in ~12 hours", random_hex()),
					'6h': ("🔔", "is due in ~6 hours", random_hex()),
					'3h': ("😡", "is due in ~3 hours - FINAL REMINDER", random_hex())
				}
				
				emoji, title_suffix, color = time_messages[reminder_threshold]
				
				embed = discord.Embed(
					title=f"{emoji} {title} {title_suffix}"[:256], 
					description="Assignment description:",
					color=color
				)
				embed.add_field(name="When", value=when_str, inline=False)
				if link:
					embed.add_field(name="Link to assignment", value=f"[Click here]({link})"[:1024], inline=False)
				if short_desc:
					embed.add_field(name="Summary", value=short_desc, inline=False)
				embed.set_thumbnail(url=image_links[random.randint(0, 2)])
				
				try:
					user = await client.fetch_user(uid)
					await user.send(f"⬇️ Bello {user.mention} :3 you have an upcoming assignment due ⬇️")
					await user.send(embed=embed)
				except discord.Forbidden:
					log.error(f'Could not DM user {uid}')
				
				db_manager.mark_assignment_reminder_sent(uid, event_id, reminder_threshold, fp)


@tasks.loop(hours = 6)
async def poll_chores():
	now = datetime.now(canvas_utils.TZ)

	all_chores = db_manager.get_due_chores()

	for chore in all_chores:
		if chore['chore_type'] == 'one_time':
			if chore['completed']:
				continue
			next_due = datetime.fromisoformat(chore['due_date'])
		else:
			if chore['last_completed']:
				last = datetime.fromisoformat(chore['last_completed'])
				next_due = last + timedelta(days = chore['frequency_days'])
			else:
				next_due = datetime.fromisoformat(chore['next_due'])
		
		time_until_due = next_due - now
		hours_until_due = time_until_due.total_seconds() / 3600
		
		reminder_type = None
		if 24 >= hours_until_due > 12:
			reminder_type = '24h'
		elif 12 >= hours_until_due > 0:
			reminder_type = '12h'
		elif hours_until_due <= 0:
			reminder_type = 'overdue'
		
		if not reminder_type:
			continue
		
		if db_manager.check_reminder_sent(chore['id'], reminder_type):
			continue
		
		try:
			user = await client.fetch_user(chore['assigned_to'])
			guild = client.get_guild(chore['guild_id']) if chore['guild_id'] else None
			
			# Customize message based on urgency
			if reminder_type == 'overdue':
				color = random_hex()
				title = f"🚨 PEE PEE POO POO: {chore['name']}"
				desc = "This chore is overdue 😡"
			elif reminder_type == '12h':
				color = random_hex()
				title = f"⏰ {chore['name']} is due in ~12 hours"
				desc = "Remember meeeeee"
			else:
				color = random_hex()
				title = f"📢 {chore['name']} is due in ~24 hours"
				desc = "Erm yeah"
			
			
			embed = discord.Embed(
				title=title[:256], 
				description=desc,
				color=color
			)
			embed.add_field(
				name="Due",
				value=next_due.strftime("%a %b %d, %Y at %I:%M %p"),
				inline=False
			)
			embed.add_field(name="List", value=chore['list_name'], inline=True)
			
			if chore['chore_type'] == 'one_time':
				embed.add_field(name="Type", value="One-time chore", inline=True)
			else:
				embed.add_field(
					name="Frequency",
					value=f"Every {chore['frequency_days']} day{'s' if chore['frequency_days'] != 1 else ''}",
					inline=True
				)
			
			embed.add_field(
				name="Mark as complete",
				value=f"`/complete list_name:{chore['list_name']} chore_number:?`",
				inline=False
			)
			
			# Send DM to assigned user
			try:
				await user.send(f"👋 Hey {user.mention}! You have a chore reminder:", embed=embed)
			except discord.Forbidden:
				log.error(f'Could not DM user {chore["assigned_to"]}')
			
			# Send to guild channel (if applicable)
			if guild:
				sent_to_channel = False
				for channel in guild.text_channels:
					if channel.permissions_for(guild.me).send_messages:
						try:
							await channel.send(f"{user.mention} - Chore reminder!", embed=embed)
							sent_to_channel = True
							break
						except discord.Forbidden:
							continue
				
				if not sent_to_channel:
					log.warning(f'Could not send chore reminder to any channel in guild {guild.id}')
			
			db_manager.mark_reminder_sent(chore['guild_id'], chore['id'], reminder_type)
			
		except discord.NotFound:
			log.error(f"User {chore['assigned_to']} not found for chore reminder")
			continue
		except Exception as e:
			log.error(f"Error sending chore reminder for chore {chore['id']}: {e}")
			continue

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
		return
	else:
		raise error
	 


client.run(token=token, log_handler=handler, log_level=logging.INFO)