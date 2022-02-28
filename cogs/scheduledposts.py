from discord.ext import tasks, commands
from datetime import datetime, timezone
import config
from cogs.fearandgreedindex import FngIndex

class Scheduledposts(commands.Cog):
	"""
	This class is for turning on, off and posting scheduled posts such as the Fear and Greed index found in main.main()
	"""

	def __init__(self, bot):
		self.bot = bot
		self.printer.start()

	def cog_unload(self):
		self.printer.cancel()

	# Loop every 15 minutes to check if the time is 12:00 A.M. - 12:29 A.M. in which time the updated fear and greed
	# index will be available. Then post the fear and greed index to the channels that have scheduled_posts turned on.
	@tasks.loop(minutes=15)
	async def printer(self):
		utc_time = datetime.now(timezone.utc)
		if utc_time.__format__("%p") == "AM" and utc_time.__format__("%H") == "12" and int(utc_time.__format__("%M")) \
				in range(0, 29, 1) and config.sched_post_chan_ids:
			fng = FngIndex(self.bot)
			fng_json = await fng.get_fngIndex()
			fng_index = fng_json[0]
			if isinstance(fng_json, list):
				for channel in config.sched_post_chan_ids:
					await channel.send("Now: " + fng_index["value_classification"] + '\n' + "FnG Index: " +
					                   fng_index["value"] + '\n' + "Last Updated: " + fng_index["timestamp"])
			else:
				for channel in config.sched_post_chan_ids:
					await channel.send("Bad request")

	# All the user to turn scheduled posts on or off for channels
	@commands.command()
	async def scheduled_posts(self, ctx: commands.Context):
		message = await ctx.send("Would you like to turn scheduled posts ON or OFF for this channel?"
		                         + "\n" + "Type -ON for on and -OFF for off.")

		response_msg = await self.bot.wait_for("message")

		if response_msg.content == "-YES":
			print("They match!")

		if response_msg.content.upper() == "-ON" and response_msg.channel == message.channel:
			config.sched_post_chan_ids.append(response_msg.channel)
			await message.delete()
			await response_msg.delete()
			await ctx.send("Scheduled messages have been turned on for this channel!")
		elif response_msg.content.upper() == "-OFF" and response_msg.channel == message.channel:
			config.sched_post_chan_ids.remove(response_msg.channel)
			await message.delete()
			await response_msg.delete()
			await ctx.send("Scheduled messages have been turned off for this channel!")
		else:
			await message.delete()
			await response_msg.delete()
			await ctx.send("Run the command again and please enter either -YES or -NO.")

def setup(bot):
	bot.add_cog(Scheduledposts(bot))
