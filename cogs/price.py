from discord.ext import commands
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import cmcidlookup, cmcpricelookup, config

class Price(commands.Cog, name="Crypto Price"):

	"""
	Controls the command(s) that get the price of cryptocurrencies.
	"""

	def __init__(self, bot: commands.Command):
		self.bot = bot

	# todo -  move the printing to a function as cogs.discordreations.on_raw_reaction_add uses the same print statement
	@commands.command()
	async def price(self, ctx: commands.Context, arg: str):

		"""
		Get the price of a cryptocurrency using its ticker.

		Example:
		    !price BTC
		"""

		requested_sym = cmcidlookup.getSymbolFromMessage(arg)

		# Try to get the requested crypto quote
		try:
			if requested_sym == "error":
				print("error")
				await ctx.send(
		            "Check the spelling of the ticker you entered. If it is correct, try again later."
		        )
			else:
				# Client and context (ctx) tuple
				cl_ctx = (self.bot, ctx)

				# Try statement for when multiple crypto share the same ticker; nothing is returned in this case
				try:
					crypto_name, quote = cmcpricelookup.getQuote(config.session, requested_sym, cl_ctx)
					await ctx.send(f"{crypto_name} Price: {quote}")
				except TypeError as e:
					print(f"Error: {e}")

		except (ConnectionError, Timeout, TooManyRedirects) as e:
			print(e)
			await ctx.send(f"Error: {e}")

def setup(bot: commands.Bot):
	bot.add_cog(Price(bot))
