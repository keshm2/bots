import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import asyncio

import logs
from logs import save_chores, load_chores, load_ids, update_ids

import aiohttp
import requests

import canvas_utils
from canvas_utils import users as _users

import random
from utils import random_hex
from utils import EmbedPaginator 
from utils import poll_ics_once


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
list_id = load_ids(id_path, log)

client = commands.Bot(command_prefix='!', intents=intents, owner_id=536044633311019009)

# -------- Owner commands ------- #


@client.event
async def on_ready():
	local_time = datetime.now()
	local_time = local_time.strftime("%m-%d-%Y %H:%M:%S")
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
@client.command(aliases=['add', 'list'])
async def newlist(ctx, *, list_name: str = None):
	await asyncio.sleep(0.2)
	chores = load_chores()
	chores.setdefault(str(ctx.author.id), [])
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
		await ctx.author.send("List will be associated with your user id divaaaa")

	def dm_check(msg: discord.Message):
		return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)
	
	await ctx.author.send("Add chores below, type \"done\" (without quotes poo poo) when you are done adding it")
	await ctx.author.send("Make sure to add each chore individually (I pee pee poo poo otherwise :( ))")
	num = 0
	while True:
		try: 
			msg = await client.wait_for("message", check=dm_check, timeout=90.0)
		
		except asyncio.TimeoutError:
			await ctx.author.send("PEE PEE POO POO CHECK 😳, you timed out (aka you took too long to add a chore)")
			break

		if msg.content.lower() == "done":
			await ctx.author.send(f"Chores saved to list {list_name}, to view the list run `showlist` (why would you want to do that??)")
			await ctx.author.send(f'There were {num} chores added... wow....')
			break

		await ctx.author.send(f"Added {msg.content} to the list, is there more 😡")
		num += 1
		chores[str(ctx.author.id)].append(msg.content)
	
	save_chores(data=chores, file_path=chores_path, append=False)
	return


@client.tree.command(name="poll_now", description="DEV TEST")
@app_commands.checks.has_permissions(administrator = True)
async def poll_now(interaction: discord.Interaction):
	await interaction.response.defer(ephemeral=True)

	if interaction.user.id != client.owner_id:
		return await interaction.followup.send(f"{interaction.user.mention} who are you?")

	else:
		now = datetime.now(canvas_utils.tz_for_user(uid=interaction.user.id))
		await poll_ics_once(
			client, _users,
			now=now,
			canvas_utils=canvas_utils,
			log=log,
			image_links=image_links,
		)

		



@client.tree.command(name = 'link_ics', description = 'Link your canvas calendar feed (.ics) for Discord reminders 📝')
@app_commands.describe(ics_link = 'Paste the link from Canvas here 🌹')
async def link_ics(interaction: discord.Interaction, ics_link: str):
	if not (ics_link.startswith('http://') or ics_link.startswith('https://')) or '.ics' and 'user' not in ics_link:
		await interaction.followup.send("That is NOT a calendar link...😡", ephemeral = True)
		await interaction.followup.send("A link looks like this: https://<link>.ics")
		return
	
	canvas_utils.set_user_ics(interaction.user.id, ics_link)

	await interaction.response.send_message('HOORAY your calendar has been saved 🤓☝️', ephemeral = True)
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
	ics = canvas_utils.get_user_ics(uid)

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
		embed_title = f"**Next upcoming {total} {"assignment" if total < 2 else "assignments"} for {interaction.user.display_name}",
		page_desc = page_desc,
		render_item = render_assignment,
		thumb_url = image_links[random.randint(0, 2)],
		timeout = 180.0
	)

	await interaction.followup.send(embed = embed._make_embed(), view = embed)
	

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
	for uid_str, cfg in list(_users.items()):
		try:
			uid = int(uid_str)
		except ValueError:
			continue

		ics_url = (cfg or {}).get('ics_link')
		if not ics_url:
			continue

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

		reminded = canvas_utils.load_reminded(uid=uid) or {} 
		changed = False

		for comp in cal.walk():
			if getattr(comp, "name", None) != 'VEVENT':
				continue

			start = canvas_utils.event_start(comp=comp, localtz=localtz)
			if not start or start <= now or start > end:
				continue

			title = str(comp.get('SUMMARY') or "No summary given").strip()
			url = canvas_utils.event_url(comp=comp)
			desc = canvas_utils.event_description(comp=comp)
			if not canvas_utils.looks_like_assignment(title=title, desc=desc, url=url):
				continue

			start_iso = start.isoformat()
			event_id = canvas_utils.event_uid(comp=comp, start_iso=start_iso)
			fp = canvas_utils.event_fingerprint(comp=comp, localtz=localtz)
			old_fp = reminded.get(event_id)

			if old_fp and old_fp != fp:
				when_str = start.strftime("%a %b %d, %I:%M %p %Z")
				link = canvas_utils.build_url(url) or url or ""
				if desc and len(desc) > 1500:
					desc = desc[:1500].rstrip() + "..."

				embed = discord.Embed(
					title=f"⏰ Due date updated: {title}",
					description="This assignment's details changed 🤯",
					color=random_hex()
				)
				embed.add_field(name="New due time", value=when_str, inline=False)
				if link:
					embed.add_field(name="**Link 🔗**", value=f"{link}", inline=False)
				if desc:
					embed.add_field(name="**📝 Summary**", value=desc, inline=False)
				embed.set_thumbnail(url=image_links[random.randint(0, 2)])

				try:
					user = await client.fetch_user(uid)
					await user.send(embed=embed)
				except discord.Forbidden as e:
					log.error(f'Could not DM user {uid}: {e}')

				reminded[event_id] = fp
				changed = True
			if reminded.get(event_id) == fp:
				continue

			if canvas_utils.remind_alert(now, start):
				when_str = start.strftime("%a %b %d, %I:%M %p %Z")
				link = canvas_utils.build_url(url) or url or ""
				short_desc = (desc[:1500].rstrip() + "...") if (desc and len(desc) > 1500) else desc

				embed = discord.Embed(
					title=f"🍂 {title} is due in ~1 day",
					description="Assignment description:",
					color=0xC79202
				)
				embed.add_field(name="When", value=when_str, inline=False)
				if link:
					embed.add_field(name="Link to assignment", value=f"[Click here]({link})", inline=False)
				if short_desc:
					embed.add_field(name="Summary", value=short_desc, inline=False)
				embed.set_thumbnail(url=image_links[random.randint(0, 2)])

				try:
					user = await client.fetch_user(uid)
					await user.send(f"⬇️ Bello {user.mention} :3 you have an upcoming assignment due ⬇️")
					await user.send(embed=embed)
				except discord.Forbidden as e:
					log.error(f'Could not DM user {uid}: {e}')

				reminded[event_id] = fp
				changed = True

		if changed:
			canvas_utils.save_reminded(uid=uid, state=reminded)



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