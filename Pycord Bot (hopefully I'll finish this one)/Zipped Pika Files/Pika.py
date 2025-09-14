import discord
from discord import client
from discord.ext import commands
import asyncio
import json
import datetime
from datetime import datetime
import pytz
from pytz import timezone
import os
from discord.utils import get
import DiscordUtils
import re

pst_time= '%m/%d/%Y %H:%M:%S %Z'
date = datetime.now(tz = pytz.utc)
date = date.astimezone(timezone('US/Pacific'))




racist = ['nigga', 'nigger', 'chink', 'beaner', 'nig', 'sex', 'haram']

def get_prefix(client,message):
	with open("prefixes.json","r") as f:
		prefixes = json.load(f)

	return prefixes[str(message.guild.id)]

def msg_contains_word(msg, word):
	return re.search(fr'\b({word})\b', msg) is not None

with open('token.txt', 'r') as file:
	x = file.read()


client = commands.Bot(command_prefix = get_prefix, intents = discord.Intents.all(), owner_id = 536044633311019009, case_insensitive = True)
client.remove_command('help')

@client.event
async def on_ready():
		print('Bot ready!')
		print('Logged on at: ' + date.strftime(pst_time))
		for filename in os.listdir('./New Cogs'):
			if filename.endswith('.py'):
				try:
					client.load_extension(f'New Cogs.{filename[:-3]}')
					print(f'Loaded {filename}')

				except Exception as e:
					print(f'Failed to load {filename}')
					print({str(e)})
		await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "Monkey Type Beat"))
	


@client.command()
@commands.is_owner()
async def logoff(ctx):
	try:
		await ctx.send('👋')
		await ctx.message.delete()
		await client.close()

	except Exception as e:
		print({str(e)})
@logoff.error
async def logoff_e(ctx, error):
	if isinstance(error, commands.FailedCheck):
		await ctx.send(f'{ctx.author.mention} you do not own this bot, this is an owner only command')
		return
		
@client.event
async def on_guild_join(guild):
	with open ("prefixes.json","r") as f:
		prefixes = json.load(f)
	prefixes[str(guild.id)] = "-"

	with open("prefixes.json","w") as f:
		json.dump(prefixes,f)



@client.command()
@commands.has_permissions(ban_members = True)
async def changeprefix(ctx,prefix):
	with open("prefixes.json","r") as f:
		prefixes = json.load(f)
	prefixes[str(ctx.guild.id)] = prefix 
	

	with open("prefixes.json","w") as f:
		json.dump(prefixes,f)
	await ctx.send(f"The prefix has been changed to `{prefix}`")
	
	
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

@activity.error
async def activity_e(ctx,error):
	if isinstance(error, commands.FailedCheck):
		msg = await ctx.send("This is an owner only command")
		await asyncio.sleep(5)
		await msg.delete()
		return
	




@client.command()
async def prefix(ctx):
	try:
		with open("prefixes.json","r") as f:
			prefixes = json.load(f)
		pre = prefixes[str(ctx.guild.id)]
		await ctx.send(f"My current prefix for this server is `{pre}`, you can change this with the `changeprefix` command. For more info please type `{pre}help`")
	except:
		pass



@client.event
async def on_message_delete(message):
	embed = discord.Embed(title = "{} deleted a message".format(message.author), description = f"**In: {message.guild.name}**", color = 0x00FFC9, timestamp = datetime.now())
	embed.add_field(name = f"Deleted message in channel {message.channel.mention}:", value = f"{message.content}", inline = True)
	channel = client.get_channel(819704984378671115)
	await channel.send(embed = embed)

@client.event
async def on_message_edit(before, after):
	embed = discord.Embed(title = f"Edited message by {before.author} in {before.guild.name}", description = f'In channel {before.channel.mention}', color = 0x7000FF, timestamp = datetime.now())
	embed.add_field(name = "**Previous message:**", value = f'{before.content}', inline = True)
	embed.add_field(name = "**Edited message:**", value = f"{after.content}", inline = True)
	channel = client.get_channel(819704984378671115)
	await channel.send(embed = embed)

@client.event
async def on_message(message):
	try:
		if message.content.lower() in racist:
			if message.author.id != client.user.id:
				with open("racism.json", "r") as f:
					racism = json.load(f)
				with open('members.json','r') as g:
					members = json.load(g)
			
				if str(message.guild.id) in racism : 
					count = racism[str(message.guild.id)]["count"]
					count = count + 1
					racism[str(message.guild.id)]["count"] = count

					with open('racism.json','w') as f:
						json.dump(racism, f)

				if str(message.guild.id) not in racism:
					racism[str(message.guild.id)] = {}
					count = [str(message.guild.id)]["count"]
					count = count + 1
					racism[str(message.guild.id)]["count"] = count

					with open('racism.json','w') as f:
						json.dump(racism, f)
					
					

				if str(message.author.id) in members:
					count = members[str(message.author.id)]["count"]
					count = count + 1
					members[str(message.author.id)]["count"] = count
					with open('members.json','w') as f:
						json.dump(members, f)

	
				if str(message.author.id) not in members:
					members[str(message.author.id)] = {}
					count = members[str(message.author.id)]["count"]
					count = count + 1
					members[str(message.author.id)]["count"] = count

					with open('members.json','w') as f:
						json.dump(members, f)
					

				
				
			embed = discord.Embed(title = '❗**Racist Word Detected** ❗', description = f'{message.author.mention} has just said a racist word, W', color = 0xFFFFFF, timestamp = datetime.now())
			embed.add_field(name = 'Racist word:', value = '{}'.format(message.content), inline = False)
			msg = await message.channel.send(embed = embed)
			await asyncio.sleep(5)
			await msg.delete()
			await client.process_commands(message)
			await client.delete.message.content()
		else:
			await client.process_commands(message)
			return
	except:
		pass
	
@client.command()
async def racism(ctx):
	with open('racism.json','r') as file:
		racism = json.load(file)
		
	with open('members.json','r') as f:
		members = json.load(f)

	count = racism[str(ctx.guild.id)]["count"]

	
	top_users = {k: v for k, v in sorted(members.items(), key = lambda item: item[1]["count"], reverse = True)}
	names = ''
	for position, user in enumerate(top_users):
		names += f'**{position + 1}** - <@!{user}> with **{top_users[user]["count"]}** racist words said\n'

	embed = discord.Embed(title = 'Total Racism count for {}'.format(ctx.guild.name), description = f'Server racism count: **{count:,}**', color = 0xC69600, timestamp = ctx.message.created_at)
	embed.add_field(name = 'Global Leaderboards: ', value = names, inline = False)
	await ctx.send(embed = embed)

'''@client.command()
async def leaderboard_racist(ctx):
	with open("members.json", "r") as file:
		leaderboard = json.load(file)

	with open("racism.json","r") as f:
		racism = json.load(f)

	count = racism[str(ctx.guild.id)]["count"]
	leaderboard = sorted(leaderboard, key=lambda x: x["count"], reverse=True)
	top_5 = leaderboard[:5]

	embed = discord.Embed(title = 'Racism Leaderboards for {}'.format(ctx.guild.name), description = 'Server racism count: {}'.format(count), color = 0xFFFFFF, timestamp = ctx.message.created_at)
	leaderboard_message = "Top 5 Leaderboard:\n"
	for i, user in enumerate(top_5):
		leaderboard_message += f"{i+1}. {user['name']}: {user["count"]}\n"
	embed.add_field(name = 'Leaderboards', value = leaderboard_message, inline = False)
	await ctx.send(embed = embed)'''
				



@client.command()
async def ping(ctx):
	msg = await ctx.send('Calculating ping...')
	await asyncio.sleep(2)
	await msg.edit(content = f'Bot ping is: `{round(client.latency * 1000)}` ms')


@client.command(aliases = ['delete','clear','c'])
@commands.has_permissions(manage_messages = True)
async def purge(ctx, amount = 10):
	await ctx.send('Purging')
	await asyncio.sleep(2)
	await ctx.channel.purge(limit = amount)
	msg = await ctx.send(f'{amount} messages deleted!')
	await asyncio.sleep(5)
	await msg.delete()
	


@client.command(aliases = ['pm'])
async def dm(ctx, member: discord.Member):
	try:
		msg = await ctx.send(f'What do you want to say to them, {ctx.author.mention}? ')
		await asyncio.sleep(2)
		def check(m):
			return m.author.id == ctx.author.id
		message = await client.wait_for('message', timeout = 10.0, check = check)
		await ctx.message.delete()
		await message.delete()
	except asyncio.TimeoutError:
		msg = await ctx.send('Time ran out, try again.')
		await asyncio.sleep(2)
		await msg.delete()
		return
	try:
		msg = await ctx.send(f'Message sent! To: {member}')
		await asyncio.sleep(2)
		await msg.delete()
		await member.send(f'{ctx.author.mention} Has a message for you: {message.content}')
		await asyncio.sleep(5)
		await ctx.channel.purge(limit = 5)

	except:
		msg = await ctx.send('The member has their dms closed, message could not be sent.')
		await asyncio.sleep(3)
		await msg.delete()

@dm.error
async def dm_e(ctx,error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.mention}, you have to mention a member to send a message to.')
		await asyncio.sleep(4)
		await ctx.channel.purge(limit = 5)

@client.command(aliases = ['m'])
@commands.has_permissions(administrator = True) 
async def mute(ctx,member : discord.Member,*,reason = "No reason provided"):
	guild = ctx.guild
	muted_role = discord.utils.get(guild.roles, name = "Muted")

	if not muted_role:
		muted_role = await guild.create_role(name = "Muted")
		
		for channel in guild.channels:
			await channel.set_permissions(muted_role, speak = False, send_messages = False, read_messages = True, read_message_history = True)


	embed = discord.Embed(description = f"{member.mention} was muted",  color = 0xDCDCDC, timestamp = ctx.message.created_at)
	embed.add_field(name = "Reason", value = reason, inline = True)
	embed.set_footer(icon_url = member.avatar_url, text = f"Muted by {ctx.author.name}")
	await member.add_roles(muted_role)
	
	
	
	msg = await ctx.send(embed=embed)
	await asyncio.sleep(5)
	await msg.delete()

@client.command(aliases=['um'])
@commands.has_permissions(administrator = True)
async def unmute(ctx,member : discord.Member,):
	guild = ctx.guild
	embed = discord.Embed(title = f"{member.mention} was unmuted", description = "You were unmuted", color = 0xBEBEBE, timestamp = ctx.message.created_at)
	embed.set_footer(icon_url = member.avatar_url, text = f"Unmuted by {ctx.author.name}")

	muted_role = discord.utils.get(guild.roles, name = "Muted")

	await member.remove_roles(muted_role)
	msg = await ctx.send(embed = embed)
	await asyncio.sleep(5)
	await msg.delete()

@client.command(aliases = ['who'])
@commands.has_permissions(manage_roles = True)
async def whois(ctx,member: discord.Member = None):
	await ctx.message.delete()
	roles = [role for role in member.roles]
	embed = discord.Embed(title="{}'s info".format(member.name), description="Member info:", timestamp = ctx.message.created_at)
	embed.add_field(name="Member's Server Nickname:", value=member.display_name, inline=False)
	embed.add_field(name="Member's ID:", value=member.id, inline=False)
	embed.add_field(name="Member's status:", value=member.status, inline=False)
	embed.add_field(name="Member's roles:", value= " ".join([role.mention for role in roles]), inline = False)
	embed.add_field(name = "Member's top role:", value = member.top_role.mention, inline = False)
	embed.add_field(name="Member joined at:", value=member.joined_at.strftime("%a %#d %B %Y, %I:%M %p UTC"), inline = False)
	embed.add_field(name="Account was created at:", value=member.created_at.strftime("%a %#d %B %Y, %I:%M %p UTC"), inline = False)
	embed.add_field(name = "Bot?", value = member.bot)
	embed.set_thumbnail(url=member.avatar_url)
	
	await ctx.send(embed = embed)

@client.command(aliases = ['h'])
async def help(ctx):
	await ctx.message.delete()
	if(commands.has_permissions(manage_roles = False)):
		embed1 = discord.Embed(title = 'Help Command Used', color = 0xFFC900, timestamp = ctx.message.created_at)
		embed1.add_field(name = f'`help`', value = 'Shows this embed', inline = False)
		embed1.add_field(name = f'`ping`', value = 'Returns bot ping', inline = False)
		embed1.add_field(name = f'`ascii`', value = 'Turns your text into ascii', inline = False)
		embed1.add_field(name = f'`covid`', value = 'Command deprecated', inline = False)
		embed1.add_field(name = f'`weather`', value = 'Shows weather for that area/city', inline = False)
		embed1.add_field(name = f'`translate <language>`', value = 'Translates following text into <language>', inline = False)
		embed1.add_field(name = f'`twitch <Name>`', value = 'Returns <Name>\'s twitch link', inline = False)
		embed1.add_field(name = f'`wiki <Argument>`', value = 'Return\'s wikipedias summary on <Argument>', inline = False)
		embed1.set_footer(icon_url = ctx.author.avatar_url, text = 'Page 1, use emojis to flip pages')

		embed2 = discord.Embed(title = 'Help Command Used - Music Help', color = 0xE0FF00, timestamp = ctx.message.created_at)
		embed2.add_field(name = '`play` <query>', value = f'Joins your voice channel and plays <query> from youtube', inline = False)
		embed2.add_field(name = '`join`', value = 'Joins your voice channel', inline = False)
		embed2.add_field(name = '`skip`', value = 'Skips the current song, note: a role named DJ is required', inline = False)
		embed2.add_field(name = '`pause`', value = 'Pauses the current song', inline = False)
		embed2.add_field(name = '`stop`', value = 'Stops the song and clears the queue', inline = False)
		embed2.add_field(name = '`queue`', value = 'Shows the queue', inline = False)
		embed2.add_field(name = '`shuffle`', value = 'Shuffles the queue', inline = False)
		embed2.add_field(name = '`remove`', value = 'Removes a song from place in queue', inline = False)
		embed2.add_field(name = '`loop`', value = 'Loops current song', inline = False)
		embed2.set_footer(icon_url = ctx.author.avatar_url, text = 'Page 2, use emojis to flip pages')

		client.pages = [embed1, embed2]
		buttons = [u'\u23EA', u'\u25C0', u'\u25B6', u'\u23E9']
		curr = 0

		msg = await ctx.send(embed = client.pages[curr])
		for button in buttons:
			await msg.add_reaction(button)
		
		try:
			reaction, user = await client.wait_for("reaction_add", check = lambda reaction, user: user == ctx.author and reaction.emoji in buttons , timeout = 60.0)
		
		except asyncio.TimeoutError:
			embed = client.pages[curr]
			embed.set_footer(text = 'Timed out.')
			await msg.clear_reactions()
		else:
			previous_page = curr

			if reaction.emoji == u'\u23EA':
				curr = 0
			elif reaction.emoji == u'\u25C0':
				if curr > 0:
					curr -= 1
			elif reaction.emoji == u'\u25B6':
				if curr < len(client.pages) - 1:
					curr += 1
			elif reaction.emoji == u'\u23E9':
				curr = len(client.pages) - 1
			
			for button in buttons:
				await msg.remove_reaction(button, ctx.author)
			
			if curr != previous_page:
				await msg.edit(embed = client.pages[curr])





@client.command(aliases = ['k'])
@commands.has_permissions(kick_members = True)
async def kick (ctx, member : discord.Member,*, reason = "Not a vibe"):
	if discord.Member == client.user:
		await ctx.send("You cant kick me, but you can manually remove me from the server if you wish!")
	else:	
		await ctx.message.delete()
		embed = discord.Embed(title = member.name + "was kicked by " + ctx.author.name, description = "Woah!", color = discord.Color.red(), timestamp = ctx.message.created_at)
		embed.add_field(name = "Reason", value = reason, inline = True)
		embed.set_thumbnail(url = member.avatar_url)
		embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Kicked by {ctx.author.name}")
		try:
			await member.send(f"You've been kicked from {guild.name}. Reason: " + reason)
		except:
			await ctx.send("The member has their dms closed, they won't know the reason for the kick")
		await member.kick(reason=reason)
		await ctx.send(embed = embed) 



@client.command(aliases=['b'])
@commands.has_permissions(ban_members = True)
async def ban(ctx,member : discord.Member,*, reason = "Totally not a vibe 🥶"):
	await ctx.message.delete()
	if member == client.user:
		await ctx.send(f'{ctx.author.mention} you cannot ban me with this command, but you can manually ban me')
	embed = discord.Embed(title = member.name + "was **banned**", description = "lmao", color = discord.Color.red())
	embed.add_field(name = "Reason", value = reason, inline = True)
	embed.set_thumbnail(url = member.avatar_url)
	embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Banned by {ctx.author.name}")
	try:
		await member.send(f"You've been banned from {guild.name}. Reason:" + reason)
	except: 
		await ctx.send("The member has their dms closed, they won't know the reason for the ban")
	await member.ban(reason=reason)
	await ctx.send(embed = embed)



@client.command(aliases = ['lock','l'])
@commands.guild_only()
@commands.has_guild_permissions(manage_channels = True)
@commands.bot_has_guild_permissions(manage_channels = True)
async def lockdown (ctx, channel: discord.TextChannel = None):
	channel = channel or ctx.channel

	if ctx.guild.default_role not in channel.overwrites:
		overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(send_messages = False)}
		

		await channel.edit(overwrites=overwrites)
		await ctx.send(f":lock: The channel {channel.name} has been locked :lock:")
	elif channel.overwrites[ctx.guild.default_role].send_messages == True or channel.overwrites[ctx.guild.default_role].send_messages == None:
		overwrites = channel.overwrites[ctx.guild.default_role]
		overwrites.send_messages = False
		await channel.set_permissions(ctx.guild.default_role, overwrite = overwrites)
		await ctx.send(f":lock: The channel {channel.name} is now locked! :lock:")



@client.command(aliases = ['release','ul'])
@commands.guild_only()
@commands.has_guild_permissions(manage_channels = True)
@commands.bot_has_guild_permissions(manage_channels = True)
async def unlock (ctx, channel: discord.TextChannel = None):
	channel = channel or ctx.channel

	if channel.overwrites [ctx.guild.default_role].send_messages == False or channel.overwrites[ctx.guild.default_role].send_messages == None:
		overwrites = channel.overwrites[ctx.guild.default_role]
		overwrites.send_messages = True
		await channel.set_permissions(ctx.guild.default_role, overwrite = overwrites)
		await ctx.send(f":unlock: The channel {channel.name} has been unlocked! :unlock:")    
	
	
	

@client.command(aliases = ['deletechan'])
@commands.has_permissions(manage_guild = True)
async def deletechannel(ctx, channel: discord.TextChannel):
	try:
		embed = discord.Embed(title = '✅ Channel Successfully Deleted! ✅', description = f'The channel `{channel}	` was deleted', timestamp = ctx.message.created_at)
		await ctx.send(embed = embed)
		await channel.delete()
	except:
		await ctx.send("The channel does not exist!")
		pass

@client.command(aliases = ['deletevc'])
@commands.has_permissions(administrator = True)
async def deletevoicechannel(ctx, channel: discord.VoiceChannel):
	try:
		e = discord.Embed(title = f'Voice channel `{channel}` was deleted', timestamp = ctx.message.created_at)
		await ctx.send(embed = e)
		await channel.delete()
	except:
		await ctx.send('The given channel does not exist')
		pass

@deletevoicechannel.error
async def dv_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		msg = await ctx.send(f'Please mention a voice channel name to delete, {ctx.author.mention}')
		await asyncio.sleep(4)
		await msg.delete()



@client.command(aliases = ['creachan'])
@commands.has_permissions(manage_guild = True)
async def createchannel(ctx, channelName):
	
	try:
		guild = ctx.guild
		embed = discord.Embed(title = '✅ Channel Successfully Created! ✅', description = "The channel `{}` was created".format(channelName), timestamp = ctx.message.created_at)
		await guild.create_text_channel(name = '{}'.format(channelName))
		await ctx.send(embed = embed)
		
	except:
		await ctx.send("An error occured while trying to run this command!")
		pass

@client.command(aliases = ['createvc'])
@commands.has_permissions(administrator = True)
async def createvoicechannel(ctx, channelName):
	try:
		guild = ctx.guild
		e = discord.Embed(title = 'Voice Channel Created!', description = 'The voice channel `{}` was created'.format(channelName), timestamp = ctx.message.created_at)
		await guild.create_voice_channel(name = '{}'.format(channelName))
		await ctx.send(embed = e)
	except:
		await ctx.send('Error occured, try again.')
		pass

client.run(f'{x}') 