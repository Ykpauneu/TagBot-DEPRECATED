import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import asyncio
import os

client = commands.Bot(command_prefix="DEBUG_PREFIX_ONLY", intents=discord.Intents.all())
client.remove_command("help")

async def database_init():
	await client.wait_until_ready()
	await client.tree.sync()
	client.db = await aiosqlite.connect("database.db")
	await client.db.execute("CREATE TABLE IF NOT EXISTS database (guild_id int, user_id int, tag_name text, tag_text text, tag_use int)")
	await client.db.commit()


async def main():
	async with client:
		await client.load_extension("cogs.client")
		await client.load_extension("cogs.tag")
		client.loop.create_task(database_init())
		await client.start("token")

asyncio.run(main())
asyncio.run(client.db.close())