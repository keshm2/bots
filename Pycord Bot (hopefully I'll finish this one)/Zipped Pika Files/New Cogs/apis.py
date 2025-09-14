import discord
import asyncio
import requests
from discord.ext import commands
import googletrans 
from googletrans import Translator 
import pyfiglet
import urllib.parse, urllib.request, re
import json
from pprint import pprint
import wikipedia 

api_key = "ab5790f7b073dbb3ea01496afaba0138"
websearch_api_key = '3d2750a1b3mshfa858bb6531ef93p161ec5jsn63c61d7c0261'

key_f = {'temp': 'Temperature', 
'feels_like': 'Feels Like',	
'temp_min': 'Todays Low',
'temp_max': 'Todays High',
'main': 'Overview',
'description': 'Description'
}


def parse_data(data):
		data = data['main']
		del data['humidity']
		del data['pressure']
		return data



def weather_message(data,location):
	location = location.title()
	message = discord.Embed(title = f"🌅{location}'s Weather 🌅", color = 0xFF5F1F)
	message.set_footer(text = 'Note all temperature data is provided in Fahrenheit, F°. Weather Data provided by Openweathermap API')
	for key in data:
		message.add_field(name = key_f[key], value = str(data[key]), inline = False)
	return message
	
def wiki_summary(arg):
		definition = wikipedia.summary(arg , sentences = 5, chars = 1750, auto_suggest = True, redirect = True)
		return definition

class apis(commands.Cog):
	def __init__(self, client):
		self.client = client




	@commands.command()
	async def covid(self,ctx,*,countryName = None):
		await ctx.message.delete()
		try:
			if countryName is None:
				em = discord.Embed(description = f"{ctx.author.mention}, you have not provided a country for statistics", colour=discord.Color.white(), timestamp = ctx.message.created_at)
				await ctx.send(embed = em)

			else:
				url = f"https://coronavirus-19-api.herokuapp.com/countries/{countryName}"
				stats = requests.get(url)
				json_stats = stats.json()
				country = json_stats["country"]
				totalCases = json_stats["cases"]
				todayCases = json_stats["todayCases"]
				totalDeaths = json_stats["deaths"]
				todayDeaths = json_stats["todayDeaths"]
				recovered = json_stats["recovered"]
				active = json_stats["active"]
				critical = json_stats["critical"]
				casesPerOneMillion = json_stats["casesPerOneMillion"]
				deathsPerOneMillion = json_stats["deathsPerOneMillion"]
				totalTests = json_stats["totalTests"]
				testsPerOneMillion = json_stats["testsPerOneMillion"]

				embed = discord.Embed(title = f"**COVID-19 Stats for {country}**", description = "🔴 **Stats are not live, but they are updated everyday!** 🔴", color = 0xFF00FF, timestamp = ctx.message.created_at)
				embed.add_field(name = "Total Cases:", value = f'{totalCases:,}', inline = True)
				embed.add_field(name = "Today's Cases:", value = f'{todayCases:,}', inline = True)
				embed.add_field(name = "Total Deaths:", value = f'{totalDeaths:,}', inline = True)
				embed.add_field(name = "Today's Deaths:", value = f'{todayDeaths:,}', inline = True)
				embed.add_field(name = "Recovered:", value = f'{recovered:,}', inline = True)
				embed.add_field(name = "Active Cases:", value = f'{active:,}', inline = True)
				embed.add_field(name = "Critical Cases:", value = f'{critical:,}', inline = True)
				embed.add_field(name = "Cases Per One Million:", value = f'{casesPerOneMillion:,}', inline = True)
				embed.add_field(name = "Deaths per One Million:", value = f'{deathsPerOneMillion:,}', inline = True)
				embed.add_field(name = f"Total Tests performed by {country}:", value = f'{totalTests:,}', inline = True)
				embed.add_field(name = "Total Tests per 1 Million:", value = f'{testsPerOneMillion:,}', inline = True)
				embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/821099536180838434/822299454040047656/unknown.png")
				await ctx.send(embed = embed)

		except Exception as e:
			em = discord.Embed(description = "Seems like there was an error running this, try again.", color = discord.Color.red(), timestamp = ctx.message.created_at)
			await ctx.send(embed = em)
			print(f'Error occured while using the covid command: {str(e)}')
	@covid.error
	async def covid_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			msg = await ctx.send(f'{ctx.author.mention}, you havent provided the correct arguments to run this.')
			await asyncio.sleep(10)
			await msg.delete()

	@commands.command()
	async def google(self,ctx):
		try:
			await ctx.message.delete()
			msg = await ctx.send('https://google.com')
			await msg.add_reaction('‼️')
		except:
			pass

		

	@commands.command(aliases = ['ascii'])
	async def asi(self,ctx,*,args):
		await ctx.message.delete()
		txt = pyfiglet.figlet_format(args)
		await ctx.send(f'```{txt}```')
	@asi.error
	async def ascii_error(self, ctx, error):
		if isinstance (error, commands.MissingRequiredArgument):
			em = discord.Embed(description = 'You are missing the required arguments to run this!', color = discord.Color.red())
			await ctx.send(embed = em)

	@commands.command(aliases = ['tr'])
	async def translate(self, ctx,lang_to,*args):
		lang_to = lang_to.lower()
		if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
			raise commmands.BadArgument(f'That is not a valid language to translate to, {ctx.author.mention}')
		text = ' '.join(args)
		translator = googletrans.Translator()
		txt_trans = translator.translate(text, dest = lang_to).text
		await ctx.send(txt_trans)
		await ctx.message.delete()

	@commands.command()
	async def yt(self,ctx,*,search):
		try:
			await ctx.message.delete()
			query_string = urllib.parse.urlencode({'search_query':search})
			htm_content = urllib.request.urlopen('http://youtube.com/results?' + query_string)
			search_results = re.findall(r"watch\?v=(\S{11})", htm_content.read().decode())
			await ctx.send(f'Here is the requested video  {ctx.author.mention},  http://youtube.com/watch?v=' + search_results[0])
		except Exception as e:
			embed = discord.Embed(description = f"An error has occured", color = discord.Color.red())
			await ctx.send(embed = embed)
			print(f"Error occured while using the Youtube Search Command: {str(e)}")
	
	@commands.command()
	async def twitch(self,ctx,*,search):
		try:
			await ctx.message.delete()
			link = 'https://twitch.tv/' + str(search)
			await ctx.send(link)
		except: 
			pass
	@twitch.error
	async def twitch_error(self,ctx,error):
		if isinstance (error,commands.MissingRequiredArgument):
			await ctx.send('https://twitch.tv.com')

	

	@commands.command()
	async def weather(self, ctx,*, location):
		try:
			await ctx.message.delete()
			if ctx.author != self.client.user:
				if len(location) >= 1:
					url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=imperial'
					data = json.loads(requests.get(url).content)
					data = parse_data(data)
					msg = await ctx.send(embed = weather_message(data,location))
		except KeyError as e:
			msg = await ctx.send(f'There was an error retrieving weather data for this location, {ctx.author.mention}')
			await asyncio.sleep(10)
			await msg.delete()
		except Exception as e:
			print({str(e)})
	@weather.error
	async def weather_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			msg = await ctx.send(f'Please enter a city to get weather data for, {ctx.author.mention}')
			await asyncio.sleep(10)
			await msg.delete()

	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def announce(self, ctx, channel: discord.TextChannel, *, msg):
		if channel == None:
			await ctx.send('Please mention a channel to send the message to.')
		await ctx.send(f'Successfully sent message: {msg}\n,  in channel {channel.mention}!')
		await channel.send(f'{msg}')
	@announce.error
	async def announce_e(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			msg = await ctx.send(f'{ctx.author.mention}, you havent provided a message or to send, or you havent specified the channel to send the message to.')
			await asyncio.sleep(10)
			await msg.delete()
		
	@commands.command()
	@commands.has_permissions(manage_guild = True)
	async def poll(self, ctx, channel: discord.TextChannel, *, msg):
		await ctx.send(f'Poll successfully started in {channel.mention}!')
		await channel.send(f'@everyone, check out this poll started by {ctx.author}! Please react with your thoughts!')
		e = discord.Embed(title = 'React with your thoughts :smile:', description = f'{msg}\n', color = 0x000080, timestamp = ctx.message.created_at)
		message = await channel.send(embed = e)
		await message.add_reaction('✅')
		await message.add_reaction('❌')
		await message.add_reaction('🤷')
	@poll.error
	async def poll_e(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f'{ctx.author.mention}, you are missing the required arguments to run this')

	
	@commands.command(aliases = ['wiki'])
	async def wikipedia(self, ctx,*,search):
		await ctx.message.delete()
		e = discord.Embed(title = f'Searching Wikipedia for {search}', description = wiki_summary(search), color = 0x099FFF)
		e.set_footer(text = 'All data provided by Wikipedia.org')
		await ctx.send(embed = e)
		if search not in wiki_summary:
			await ctx.send(f"{ctx.author.mention}, the provided search query is not in Wikipedias database")
		

	@wikipedia.error
	async def wikipedia_e(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			msg = await ctx.send(f'{ctx.author.mention} please enter a search term to search for')
			await asyncio.sleep(5)
			await msg.delete()
	
def setup(client):
	client.add_cog(apis(client))