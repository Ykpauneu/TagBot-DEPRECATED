import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import *
import json
import aiosqlite
import math

class PermissionsChecker():
	def __init__(self, client):
		self.client = client

	async def is_administrator(self, user):
		return user.guild_permissions.administrator

	async def is_guild(self, context):
		return context.guild

			# embed = discord.Embed(title='Ошибка',description = "Эта команда доступна только на сервере", colour=0xff0000)
			# embed.set_author(name="⚔️ | Кланы")
			# await interaction.followup.send(embed=embed)
			# return		