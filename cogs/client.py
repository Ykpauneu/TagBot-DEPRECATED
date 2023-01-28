import discord
from discord.ext import commands

class ClientCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Loaded as {self.client.user}")


	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		await self.client.db.execute("DELETE FROM database WHERE guild_id = ?", (guild.id, ))
		await self.client.db.commit()


	@commands.Cog.listener()
	async def on_member_remove(self, member):
		await self.client.db.execute("DELETE FROM database WHERE user_id = ?", (member.id, ))
		await self.client.db.commit()


async def setup(client):
	await client.add_cog(ClientCog(client))