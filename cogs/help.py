from typing import Optional
from discord.ext import commands
from discord import Embed
from typing import Set

# Don't ask how this all works. Copied most. Still trying to understand.
class HelpCommand(commands.MinimalHelpCommand):
	def get_command_signature(self, command: commands.Command):
		return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

	async def _help_embed(self, title: str, description: Optional[str] = None, mapping: Optional[dict] = None,
	                      command_set: Optional[Set[commands.Command]] = None):
		embed = Embed(title=title)
		if description:
			embed.description = description

		avatar = self.context.bot.user.avatar or self.context.bot.user.default_avatar
		embed.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.avatar_url)

		if command_set:
			# Show help about all commands in the set
			filtered = await self.filter_commands(command_set, sort=True)
			for command in filtered:
				embed.add_field(
					name=self.get_command_signature(command),
					value=command.short_doc or "...",
					inline=False)
		elif mapping:
			# Add a short description of commands in each cog
			for cog, command_set in mapping.items():
				filtered = await self.filter_commands(command_set, sort=True)
				if not filtered:
					continue
				name = cog.qualified_name if cog else "No category"
				# \u2002 is a unicode character for a space
				cmd_list = "\u2002".join(f"'{self.clean_prefix}{cmd.name}'" for cmd in filtered)
				value = (f"{cog.description}\n{cmd_list}" if cog and cog.description else cmd_list)
				embed.add_field(name=name, value=value)
		return embed

	async def send_bot_help(self, mapping: dict):
		embed = await self._help_embed(title="Bot Commands", description=self.context.bot.description, mapping=mapping)
		await self.get_destination().send(embed=embed)
	async def send_command_help(self, command: commands.Command):
		embed = await self._help_embed(title=command.qualified_name, description=command.help,
		                               command_set=command.commands if isinstance(command, commands.Group) else None)
		await self.get_destination().send(embed=embed)

	async def send_cog_help(self, cog: commands.Cog):
		embed = await self._help_embed(title=cog.qualified_name, description=cog.description,
		                               command_set=cog.get_commands())
		await self.get_destination().send(embed=embed)

	send_group_help = send_command_help

class HelpCog(commands.Cog, name="Help"):
	"""
	Shows help info about commands.
	"""

	def __init__(self, bot: commands.Bot):
		self.original_help_command = bot.help_command
		bot.help_command = HelpCommand()
		bot.help_command.cog = self

	def cog_unload(self):
		self.bot.help_command = self.original_help_command

def setup(bot: commands.Bot):
	bot.add_cog(HelpCog(bot))
