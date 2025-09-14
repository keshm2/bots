import discord
import traceback
import sys
from discord.ext import commands


class CommandErrorHandler(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""The event triggered when an error is raised while invoking a command.
		Parameters
		------------
		ctx: commands.Context
			The context used for command invocation.
		error: commands.CommandError
			The Exception raised.
		"""
		if hasattr(ctx.command, 'on_error'):
			return

		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		ignored = (commands.CommandNotFound, )
		error = getattr(error, 'original', error)

		if isinstance(error, ignored):
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f'{ctx.command} has been disabled.')

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.BadArgument):
			if ctx.command.qualified_name == 'tag list':
				await ctx.send('I could not find that member. Please try again.')

		else:
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	@commands.command(name='repeat', aliases=['mimic', 'copy', 'echo'])
	async def copy(self, ctx, *, inp: str):
		"""A simple command which repeats your input!
		Parameters
		------------
		inp: str
			The input you wish to repeat.
		"""
		await ctx.message.delete()
		await ctx.send(inp)

	@copy.error
	async def copy_error(self, ctx, error):
		"""A local Error Handler for our command do_repeat.
		This will only listen for errors in do_repeat.
		The global on_command_error will still be invoked after.
		"""

		if isinstance(error, commands.MissingRequiredArgument):
			if error.param.name == 'inp':
				await ctx.send("You forgot to give me input to repeat!")
	
	@commands.command()
	async def av(self, ctx, member: discord.Member):
		e = discord.Embed(title = f"{member}'s Avatar", color = 0xB2FF00)
		e.set_image(url = f'{member.avatar_url}')
		await ctx.send(embed = e)

	@av.error
	async def av_error(self, ctx, error):
		if isinstance (error, commands.MissingRequiredArgument):
			e = discord.Embed(title = f"{ctx.author}'s Avatar", color = 0xD3FFDF)
			e.set_image(url = f"{ctx.author.avatar_url}")
			await ctx.send(embed = e)
	



def setup(client):
	client.add_cog(CommandErrorHandler(client))
	