import discord
import asyncio 
import datetime
from datetime import datetime
import random
from discord.ext import commands
import json
import requests
import os
import praw
from pathlib import Path

intents = discord.Intents.default()
intents.members = True
def get_prefix(client,message):
	with open("D:/Python/Bot/Add-Ons and Utils/prefixes.json","r") as f:
		prefixes = json.load(f)

	return prefixes[str(message.guild.id)]
cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f'{cwd}\n-----')

fmt = '%#c'



client = commands.Bot(command_prefix = get_prefix,
 intents = intents,
 owner_id = 536044633311019009,
 case_insensitive = True
 )
client.remove_command('help')
token = 'ODE4NjYyMjUwMjE4MTI3MzYx.YEbUog.wIXi9FQtZoMBk4th9f_abddz8IA'
client.blacklisted_users = []

def read_json(filename):
	with open(f'{cwd}/Add-Ons and Utils/blacklist.json', 'r') as file:
		data = json.load(file)
	return data 
def write_json(data, filename):
	with open(f'{cwd}/Add-Ons and Utils/blacklist.json', 'w') as file:
		json.dump(data, file, indent = 4)	



banned_words = ["nigga","nigger","Nigger","Nigga",]
@client.event
async def on_ready():
	time = datetime.datetime.now()
	print(f'Online at {time}')
	print('')
	print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(client))
	await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "@Akima"))


	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			try:
				client.load_extension(f'cogs.{filename[:-3]}')
				print(f"Loaded {filename}")
			except Exception as e:
				print(f"Failed to load {filename}")
				print(f"Error: {e}")
	try:
		data = read_json("blacklist")
		client.blacklisted_users = data[""]
	except:
		pass



@client.event
async def blacklisted(message, user: discord.Member):
	with open(f'{cwd}/Add-Ons and Utils/blacklist.json', 'r') as file:
		if user.id in file and message.content.starts_with(f'{pre}'):
			await message.channel.send('Hey, you have been blacklisted, you cannot use any commands.')
			await ctx.message.delete()

@client.command()
@commands.is_owner()
async def logoff(ctx):
	try:
		await ctx.message.delete()
		msg = await ctx.send(f'{ctx.author.mention}, I am now going offline')
		await msg.add_reaction('👋')
		await client.logout()

	except Exception as e:
		print({str(e)})
@logoff.error
async def logoff_e(ctx, error):
	if isinstance(error, commands.FailedCheck):
		await ctx.send(f'{ctx.author.mention} you do not own this bot, this is an owner only command')
		

@client.event
async def on_message(message):
	if message.author.id == client.user.id:
		return
	if message.author.id in client.blacklisted_users:
		return
	if 'help' in message.content.lower():
		await message.channe.send('Hey :) Seems like you are having trouble, why dont you try using the help command?')

	await client.proccess_commands(message)

@client.command()
@commands.has_permissions(manage_guild = True)
async def blacklist(ctx, user: discord.Member):
	if user.id == ctx.author.id:
		await ctx.send('You cannot blacklist yourself')
	elif user.id == client.user.id:
		await ctx.send('You cannot blacklist the bot')
	else:
		client.blacklisted_users.append(user.id)
		data = read_json("blacklist")
		data['blacklistedUsers'].append(user.id)
		write_json(data, "blacklist")
		await ctx.send(f'I have blacklisted {user.name} for you {ctx.author}')

@client.command()
@commands.has_permissions(manage_guild = True)
async def unblacklist(ctx, user: discord.Member):
	client.blacklisted_users.remove(user.id)
	data = read_json("blacklist")
	data['blacklistedUsers'].remove(user.id)
	write_json(data, "blacklist")
	await ctx.send(f'I have unblacklisted {user.name} for you {ctx.author}')


@client.command(name = 'Load Cog', description = 'Loads cogs')
@commands.has_permissions(ban_members = True)
async def loadcog(ctx, cogname = None):
	if cogname is None:
		await ctx.send("Please provide a cog name!")
		return
	try:
		client.load_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not load cog {cogname}: {str(e)}')
	else:
		await ctx.send(f'Loaded {cogname} successfully!')

@client.command()
@commands.has_permissions(ban_members = True)
async def unloadcog(ctx, cogname = None):
	if cogname is None:
		await ctx.send("Please provide a cog name!")
		return
	try:
		client.unload_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not unload cog {cogname}: {str(e)}')
	else:
		await ctx.send(f'Unloaded {cogname} successfully!')



@client.event
async def on_message(msg):
	for word in banned_words:
		if word in msg.content:
			await msg.delete()
			
	await client.process_commands(msg)

@client.event
async def on_guild_join(guild):
	with open ("prefixes.json","r") as f:
		prefixes = json.load(f)
	prefixes[str(guild.id)] = "~"

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


@client.event
async def on_message(msg):
	try:
		if msg.mentions[0] == client.user:
			with open("prefixes.json","r") as f:
				prefixes = json.load(f)
			pre = prefixes[str(msg.guild.id)]
			await msg.channel.send(f"My current prefix for this server is `{pre}`, you can change this with the `changeprefix` command. For more info please type `{pre}help`")
	except:
		pass

	await client.process_commands(msg)

@client.command(aliases=['user','info'])
@commands.has_permissions(kick_members = True)
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

@client.command(aliases = ['delchan'])
@commands.has_permissions(manage_guild = True)
async def deletechannel(ctx, channel: discord.TextChannel):
	try:
		embed = discord.Embed(title = '✅ Channel Successfully Deleted! ✅', description = f'The channel `{channel}	` was deleted', timestamp = ctx.message.created_at)
		await ctx.send(embed = embed)
		await channel.delete()
	except:
		await ctx.send("The channel does not exist!")
		pass


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




@client.command()
@commands.has_permissions(send_messages = True)
async def ping(ctx):
	await ctx.message.delete()
	e = discord.Embed(description = f"🏓 Bot ping: `{round(client.latency * 1000)}` ms 🏓", color = ctx.author.color)
	e.add_field(name = 'More info:', value = ':information_source: Still having problems? Check your internet speed here: [Speed Test](https://speedtest.net)', inline = False)
	await ctx.send(embed = e)


@client.command(aliases = ['pm'])
async def dm(ctx, member: discord.Member):
	e2 = discord.Embed(description = f'What do you want to say to them, {ctx.author.mention}?')
	await ctx.send(embed = e2)
	def check(m):
		return m.author.id == ctx.author.id
	message = await client.wait_for('message', check = check)
	try:
		e = discord.Embed(description = f'Message sent! To: {member}', color = discord.Color.teal())
		await ctx.send(embed = e)
		await member.send(f'{ctx.author.mention} Has a message for you: \n {message.content}')
	except:
		e = discord.Embed(description = 'The member has their dms closed, message could not be sent', color = discord.Color.red(), timestamp = ctx.message.created_at)
		await ctx.send(embed = e)
		if discord.Member == client.user:
			await ctx.send(f'You cannot dm me, {ctx.author.mention}')







@client.command(aliases = ['c', 'purge'])
@commands.has_permissions(manage_messages = True)
async def clear (ctx, amount = 10):
	await ctx.channel.purge(limit = amount + 1 )
	await ctx.send(f"`{amount}` message(s) has been deleted! :thumbsup:" )
	await asyncio.sleep(3)
	await ctx.channel.purge(limit = amount)
	


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



@client.command(aliases=['m'])
@commands.has_permissions(kick_members = True) 
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
	
	
	
	await ctx.send(embed=embed)
	
	


@client.command(aliases=['um'])
@commands.has_permissions(kick_members = True)
async def unmute(ctx,member : discord.Member,):
	try:
		guild = ctx.guild
		embed = discord.Embed(title = f"{member.mention} was unmuted", description = "You were unmuted", color = 0xBEBEBE, timestamp = ctx.message.created_at)
		embed.set_thumbnail(url = member.avatar_url)
		embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Unmuted by {ctx.author.name}")

		muted_role = discord.utils.get(guild.roles, name = "Muted")

		await member.remove_roles(muted_role)
		await ctx.send(embed = embed)
	except Exception as e:
		em = discord.Embed(description = "Something went wrong while attempting this command", color = discord.Color.red())
		print(f'Error occured while using the unmute command: {str(e)}')
		await ctx.send(embed = em)
@client.command()
async def serverinfo(ctx):
	await ctx.message.delete()
	name = str(ctx.guild.name)
	description = str(ctx.guild.description)
	owner = str(ctx.guild.owner)
	guild_id = str(ctx.guild.id)
	region = str(ctx.guild.region)
	memberCount = str(ctx.guild.member_count)
	icon = str(ctx.guild.icon_url)
	if description == None:
		description = "There is no description for this server"
	embed = discord.Embed(title = "Server Info", description = description, color = 0xffff00, timestamp = ctx.message.created_at)
	embed.add_field(name = 'Owner', value = owner, inline = True)
	embed.add_field(name = 'Server ID', value = guild_id, inline = True)
	embed.add_field(name = 'Server Region', value = region, inline = True)
	embed.add_field(name = 'Member Count', value = memberCount, inline = True)
	embed.set_footer(url = icon)

	await ctx.send(embed = embed)

@client.event
async def on_member_join(member, guild):  
	e = discord.Embed(title = f'Welcome, {member.mention}, to {guild.name}', description = 'Enjoy your stay!', color = discord.Color.teal())
	await member.send(embed = e)








client.run(token)  