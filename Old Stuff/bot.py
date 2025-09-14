import discord
import asyncio 
import datetime
import random
from discord.ext import commands
import json
import os

client = commands.Bot(command_prefix = "x")
client.remove_command('help')


@client.command(aliases=['c','purge'])
@commands.has_permissions(manage_messages = True)
async def clear(ctx,amount=5):
	await ctx.channel.purge(limit=amount)

@client.command(aliases=['k'])
@commands.has_permissions(kick_members = True)
async def kick(ctx,member : discord.Member,*, reason = "Being TOO nerdy"):

	embed = discord.Embed(title = member.name + "was kicked by " + ctx.author.name, description = "Nerd has been :sparkles: expelled :sparkles:", color = discord.Color.blue())
	embed.add_field(name = "Reason", value = reason, inline = True)
	embed.set_thumbnail(url = member.avatar_url)
	embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Kicked by {ctx.author.name}")
	try:
		await member.send("You've been kicked from The Bedroom. Reason: " + reason)
	except:
		await ctx.send("The member has their dms closed, they won't know the reason for the kick")
	await member.kick(reason=reason)
	await ctx.send(embed = embed) 




@client.command(aliases=['b'])
@commands.has_permissions(ban_members = True)
async def ban(ctx,member : discord.Member,*, reason = "Being a shitty human"):

	embed = discord.Embed(title = member.name + "was **banned**", description = ":sparkles: Toxic shit belongs NOWHERE in the vibe area :sparkles:", color = discord.Color.blue())
	embed.add_field(name = "Reason", value = reason, inline = True)
	embed.set_thumbnail(url = member.avatar_url)
	embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Banned by {ctx.author.name}")
	try:
		await member.send("You've been banned from The Bedroom. Reason:" + reason)
	except: 
		await ctx.send("The member has their dms closed, they won't know the reason for the ban")
	await member.ban(reason=reason)
	await ctx.send(embed = embed)


@client.command(aliases=['m'])
@commands.has_permissions(kick_members = True) 
async def mute(ctx,member : discord.Member,*,reason = "No reason provided"):
	

	embed = discord.Embed(title = member.mention + " was muted", description = "You were muted",  color = discord.Color.red())
	embed.add_field(name = "Reason", value = reason, inline = True)
	embed.set_thumbnail(url = member.avatar_url)
	embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Muted by {ctx.author.name}")
	muted_role = ctx.guild.get_role(761770489529237558)
	
	await member.add_roles(muted_role)
	
	await ctx.send(embed=embed)
	await ctx.send(reason=reason)
	


@client.command(aliases=['um'])
@commands.has_permissions(kick_members = True)
async def unmute(ctx,member : discord.Member,):

	embed = discord.Embed(title = member.mention + " has been unmuted", description = "You were unmuted", color = discord.Color.red())
	embed.set_thumbnail(url = member.avatar_url)
	embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Unmuted by {ctx.author.name}")

	muted_role = ctx.guild.get_role(761770489529237558)

	await member.remove_roles(muted_role)
	await ctx.send(embed = embed)

@client.command(aliases=['user','info'])
@commands.has_permissions(kick_members = True)
async def whois(ctx,member: discord.Member):
	embed = discord.Embed(title="{}'s info".format(member.name), description="Member info:")
	embed.add_field(name="Name", value=member.name, inline=True)
	embed.add_field(name="ID", value=member.id, inline=True)
	embed.add_field(name="Status", value=member.status, inline=True)
	embed.add_field(name="Highest Role", value=member.roles)
	embed.add_field(name="Joined", value=member.joined_at)
	embed.add_field(name="Created", value=member.created_at)
	embed.set_thumbnail(url=member.avatar_url)
	client.get_channel(821099536180838434)

	await ctx.send( embed = embed)

@client.command(aliases = ['mhelp'])
@commands.has_permissions(kick_members = True)
async def modhelp(ctx):
	embed = discord.Embed(title = "Welcome to Bedtime Bot V2!", description = "Moderation/Admin Console Commands", color = discord.Color.green())
	embed.set_author(name = "Created by: Keshy#0533, more mod commands coming soon!")
	embed.add_field(name = "MODERATION CMMDS", value = "These commands can only be used by mods and above, prefix is 'x', and there should be no spaces after the letter (ex: xmute)", inline = False)
	embed.add_field(name = "Ping(alias = xp)", value = "Shows bot's latency", inline = True)
	embed.add_field(name = "Modhelp(aliases = xmhelp, or xmodhelp)", value = "Shows this menu", inline =True)
	embed.add_field(name = "Mute(alias = xm)", value = "Mutes a user", inline = True)
	embed.add_field(name = "Ban(alias = xb)", value = "Bans a user, can be with or without reason", inline = True)
	embed.add_field(name = "Kick(alias = xk)", value = "Kicks a user, can be with or without reason", inline = True )
	embed.add_field(name = "Giveaway(aliases = xgiveaway or xg)", value = "Creates and starts a giveaway, giveaway is in minutes btw, and currently there will only be one winner, more winners code to be added soon!", inline = True)
	embed.add_field(name = "User, or Whois(aliases = xuser or xwhois)", value = "Displays information about a user", inline = True)
	embed.add_field(name = "Lock(aliases = xl or xlock)", value = "Locks a channel from being accessed", inline = True)
	embed.add_field(name = "Unban(alias = xub)", value = "Unbans a member", inline = True)
	embed.add_field(name = "Unlock(aliases = xrelease or xul)", value = "Unlocks a channel", inline = True)
	embed.add_field(name = "Purge(alias = xclear)", value = "Purges a set amount of messages (default is 5, auto-purging coming soon!)", inline = True)
	embed.add_field(name = "Rule # (ex: xrule 1)", value = "Replies with the rule, (up to seven total)", inline = True)
	embed.add_field(name = "Warn", value = "Warns a user (duh), to be added soon!", inline = True)
	embed.add_field(name = "Check warns", value = "Checks how many warns a user has(json file to be added soon!)", inline = True)
	embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.name}")
	await ctx.send(embed=embed)


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

@client.command(aliases = ['p'])
@commands.has_permissions(send_messages = True)
async def ping(ctx):
	await ctx.send(f"Bot ping: {round(client.latency * 1000)} ms")

def convert(time):
	pos = ["s","m","h","d"]

	time_dict = {"s": 1, "m" : 60, "h" : 3600, "d" : 3600*24}

	unit = time[-1]

	if unit not in pos:
		return -1
	try:
		val = int(time[:-1])
	except:
		return -2

	return val * time_dict[unit]

@client.command(aliases = ['giveaway','g'])
@commands.has_permissions(kick_members = True)
async def gstart(ctx):
	await ctx.send("Giveaway has been started! Answer the following questions within a minute before you are timed out and the giveaway is cancelled")
	questions = ["Which channel will this be hosted in?","How long will this giveaway last? In seconds, minutes, hours, or days please",
	"What is the prize of this giveaway?"]

	answers = []

	def check(m):
		return m.author == ctx.author and m.channel == ctx.channel

	for i in questions:
		await ctx.send(i)

		try:
			msg = await client.wait_for('message', timeout = 60.0, check = check)
		except asyncio.TimeoutError:
			await ctx.send('You didnt answer in time :c')
			return
		else:
			answers.append(msg.content)
	try:
		c_id = int(answers[0][2:-1])
	except:
		await ctx.send(f"No channel mentioned! Incase you didnt know, you actually have to mention a channel to send this giveaway to, e.g {ctx.channel.mention}")
		return
	channel = client.get_channel(c_id)

	time = convert(answers[1])
	if time == -1:
		await ctx.send(f"You didnt answer with a proper time unit. Use (s|m|h|d) to abriviate")
		return
	elif time == -2:
		await ctx.send(f"The time must be a number, doesn't work with letters bruv(how did you misunderstand that time is in numbers lmao)")
		return
	prize = answers[2]

	await ctx.send(f"The Giveaway will be in {channel.mention} and will last {answers[1]}")

	embed = discord.Embed(title = "Giveaway!", description = f"{prize}", color = ctx.author.color)
	embed.add_field(name = "Hosted by:", value = ctx.author.mention)
	embed.set_footer(text = f"Ends {answers[1]} from now!")
	my_msg = await channel.send(embed = embed)
	await my_msg.add_reaction("🎉")
	await asyncio.sleep(time)
	new_msg = await channel.fetch_message(my_msg.id)
	users = await new_msg.reactions[0].users().flatten()
	users.pop(users.index(client.user))
	winner = random.choice(users)
	await channel.send(f"Congratulations! {winner.mention} won the {prize}!")

@client.command(aliases = ['re'])
@commands.has_permissions(kick_members = True)
async def reroll(ctx, channel :discord.TextChannel, id_ : int):
	try:
		new_msg = await channel.fetch_message(id_)
	except:
		await ctx.send("The ID was entered incorrectly.")
		return
	users = await new_msg.reactions[0].users().flatten()
	users.pop(users.index(client.user))
	winner = random.choice(users)

	await channel.send(f"Congratulations! The new winner is {winner.mention}. They won the {prize}!")
		




#banned_words = ["nigga","nigger","Nigger","Nigga",]



	#embed = discord.Embed(title="{}'s info".format(member.name), description="Welcome to {}".format(member.guild.name))
	#embed.add_field(name="Name", value=member.name, inline=True)
	#embed.add_field(name="ID", value=member.id, inline=True)
	#embed.add_field(name="Status", value=member.status, inline=True)
	#embed.add_field(name="Roles", value=member.top_role)
	#embed.add_field(name="Joined", value=member.joined_at)
	#embed.add_field(name="Created", value=member.created_at)
	#embed.set_thumbnail(url=member.avatar_url)
	#inlul = client.get_channel(763122994461409295)

	#await inlul.send(inlul, embed=embed)
#@client.event
#async def on_member_remove(member):
   #await client.get_channel(idchannel).send(f"{member.name} has left")

#@client.event
#async def on_message(msg):
	#for word in banned_words:
		#if word in msg.content:
			#await msg.delete()

	#await client.process_commands(msg)









client.run("NzYzMTIyNzMxMjMwOTUzNDcy.X3zHbQ.AsnbuBE29ebJQRwFYKiItmwJqBc")   