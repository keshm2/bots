import discord
import asyncio 
import datetime
from datetime import datetime
import pytz
from pytz import datetime
import random
import json
import requests
import os
import utils
from discord.ext import commands
from discord.ext.buttons import Paginator


		

  

class mods(commands.Cog):
	def __init__(self,client):
		self.client = client
		
	@commands.command
	async def help(ctx):
		await ctx.send('Command still in progress.')
	

	

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def toggle(self, ctx, *, command):
		try:
			command = self.client.get_command(command)
			if command is None:
				msg = await ctx.send(f"{ctx.author.mention} I couldn't find a command with that name")
				await asyncio.sleep(10)
				await msg.delete()
			elif ctx.command == command:
				await ctx.send(f"{ctx.author.mention} you cannot disable this command.")
			else:
				command.enabled = not command.enabled
				ter = "enabled" if command.enabled else "disabled"
				await ctx.send(f'I have {ter} command {command.qualified_name}, {ctx.author.mention}')
				if command.enabled == False:
					with open('toggled.txt','a') as file:
						file.write(f'{datetime.datetime.now()} - Command disabled by {ctx.author}: {command.qualified_name} \n')
				if command.enabled == True:
					with open('toggled.txt', 'a') as file:
						file.write(f'{datetime.datetime.now()} - Command enabled by {ctx.author}: {command.qualified_name} \n')
		except:
			pass

	@toggle.error
	async def toggle_e(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			msg = await ctx.send(f'{ctx.author.mention} please mention a command to toggle')
			await asyncio.sleep(10)
			await msg.delete()
def setup(client):
	client.add_cog(mods(client))
