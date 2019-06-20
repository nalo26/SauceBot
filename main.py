import discord
import aiohttp
from discord.ext import commands

TOKEN = "past your Discord bot token here"
PREFIX = '.'

client = commands.Bot(command_prefix = PREFIX)

@client.event
async def on_ready():
	print(f'Logged in as {client.user.name}#{client.user.discriminator}')
	print('-------------------')

@client.event
async def on_command_error(ctx, error):
	print(error)

@client.command(aliases=['sauce', 'saucenao'])
async def source(ctx, *, to_source:str=None):
	# Get the last image
	if not to_source:
		image_url = None
		def f(mes):
			return all([
				not mes.author.bot,
				len(mes.embeds) or len(mes.attachments),
			])
		async for message in ctx.channel.history(limit=100).filter(f):
			to_search = message.attachments or message.embeds
			try:
				image_url = to_search[0].thumbnail.proxy_url
			except AttributeError:
				image_url = to_search[0].proxy_url
			break
	else:
		image_url = to_source

	if not image_url:
		await ctx.send('No images could be found in the chat')
		return

	url = 'https://saucenao.com/search.php'
	params = {
		'output_type': 2,
		'url': image_url,
		# 'numres': 1,  # limit
		'api_key': 'your sauceNAO API key here',
	}

	async with aiohttp.ClientSession() as session:
		async with session.get(url, params=params) as r:
			data = await r.json()
	try: 
		result = data['results'][0]
	except Exception: 
		await ctx.send('No results for this query')
		return
	if float(result['header']['similarity']) > 50:
		e = discord.Embed(name="", description="", colour=0xFFFFFF)
		try: e.set_author(name=result['data']['author_name'], url=result['data']['author_url'])
		except Exception: pass

		try: e.add_field(name='Title', value=result['data']['title'])
		except Exception: pass

		e.add_field(name='Similarity', value=result['header']['similarity']+'%')
		e.add_field(name='URL', value=result['data']['ext_urls'][0])
		e.set_image(url=result['header']['thumbnail'])

		await ctx.send(embed=e)
	else:
		await ctx.send('No good results for this query')

client.run(TOKEN)