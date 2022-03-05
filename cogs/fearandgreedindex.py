from discord.ext import commands
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json, config

fng_url = "https://api.alternative.me/fng/?limit=10&format=json&date_format=us"

class FngIndex(commands.Cog, name="Fear and Greed Index"):
	"""
	Gets the Fear and Greed Index.
	"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	# Command for getting the current fear and greed index and print it out
	@commands.command()
	async def fng(self, ctx: commands.Context):
		"""
		Show today's Fear and Greed Index.
		"""
		fng_json = await self.get_fngIndex()
		if isinstance(fng_json, list):
			fng_index = fng_json[0]
			await ctx.send(
				"Now: " + fng_index["value_classification"] + '\n' + "FnG Index: " + fng_index["value"] + '\n'
				+ "Last Updated: " + fng_index["timestamp"])
			await ctx.send("https://alternative.me/crypto/fear-and-greed-index.png")

		else:
			await ctx.send("Bad request")

	# Command for getting yesterday's fear and greed index and print it out
	@commands.command()
	async def yfng(self, ctx: commands.Context):
		"""
		Show yesterday's Fear and Greed Index.
		"""
		fng_json = await self.get_fngIndex()
		if isinstance(fng_json, list):
			fng_index = fng_json[1]
			await ctx.send(
				"Yesterday: " + fng_index["value_classification"] + '\n' + "FnG Index: " + fng_index["value"])
		else:
			await ctx.send("Bad request")

	# See cogs.scheduledposts for scheduled for scheduled posting
	async def get_fngIndex(self):
		try:
			response = config.session.get(fng_url)
			json_data = json.loads(response.text)
			fng_list = json_data["data"]
			return fng_list
		except (ConnectionError, Timeout, TooManyRedirects) as e:
			print(e)
			return

def setup(bot: commands.Bot):
	bot.add_cog(FngIndex(bot))
