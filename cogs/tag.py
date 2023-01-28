import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import asyncio
import random
from .libs import permissonschecker

class Search(discord.ui.View):
	def __init__(self, client, author, name):
		super().__init__()
		self.client = client
		self.author = author
		self.name = name
		self.limit = 10
		self.offset = 0
		self.current_page = 1
		self.max_pages = 10


	async def interaction_check(self, interaction:discord.Interaction):
		return self.author == interaction.user.id


	@discord.ui.button(label="⇐", custom_id="left_max", style=discord.ButtonStyle.blurple)
	async def left_max(self, interaction:discord.Interaction, button:discord.ui.Button):
		if button.custom_id == "left_max":
			self.offset = 0
			self.current_page = 1

			embed=discord.Embed(title=f'Поиск **{self.name}** ({self.current_page}/{self.max_pages})',description="", colour=discord.Colour.default())
			async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name LIKE ? OR tag_name LIKE ? ORDER BY tag_use DESC LIMIT ? OFFSET ?", (interaction.guild.id, '%'+self.name+'%', self.name, self.limit, self.offset)) as cursor:
				async for rows in cursor:
					embed.description += f"{rows[0]}\n"

				await interaction.response.edit_message(embed=embed, view=self)


	@discord.ui.button(label="←", custom_id="left", style=discord.ButtonStyle.blurple)
	async def left(self, interaction:discord.Interaction, button:discord.ui.Button):
		if button.custom_id == "left":
			if self.offset > 0:
				self.offset = self.offset - 10
				self.current_page = self.current_page - 1
			else:
				self.offset = 0
				self.current_page = 1

			embed=discord.Embed(title=f'Поиск **{self.name}** ({self.current_page}/{self.max_pages})',description="", colour=discord.Colour.default())
			async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name LIKE ? OR tag_name LIKE ? ORDER BY tag_use DESC LIMIT ? OFFSET ?", (interaction.guild.id, '%'+self.name+'%', self.name, self.limit, self.offset)) as cursor:
				async for rows in cursor:
					embed.description += f"{rows[0]}\n"

				await interaction.response.edit_message(embed=embed, view=self)


	@discord.ui.button(label="→", custom_id="right", style=discord.ButtonStyle.blurple)
	async def right(self, interaction:discord.Interaction, button:discord.ui.Button):
		if button.custom_id == "right":
			if self.offset < 90:
				self.offset = self.offset + 10
				self.current_page = self.current_page + 1
			else:
				self.offset = 90
				self.current_page = self.max_pages

			embed=discord.Embed(title=f'Поиск **{self.name}** ({self.current_page}/{self.max_pages})',description="", colour=discord.Colour.default())
			async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name LIKE ? OR tag_name LIKE ? ORDER BY tag_use DESC LIMIT ? OFFSET ?", (interaction.guild.id, '%'+self.name+'%', self.name, self.limit, self.offset)) as cursor:
				async for rows in cursor:
					embed.description += f"{rows[0]}\n"

				await interaction.response.edit_message(embed=embed, view=self)


	@discord.ui.button(label="⇒", custom_id="right_max", style=discord.ButtonStyle.blurple)
	async def right_max(self, interaction:discord.Interaction, button:discord.ui.Button):
		if button.custom_id == "right_max":
			self.offset = 90
			self.current_page = self.max_pages

			embed=discord.Embed(title=f'Поиск **{self.name}** ({self.current_page}/{self.max_pages})',description="", colour=discord.Colour.default())
			async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name LIKE ? OR tag_name LIKE ? ORDER BY tag_use DESC LIMIT ? OFFSET ?", (interaction.guild.id, '%'+self.name+'%', self.name, self.limit, self.offset)) as cursor:
				async for rows in cursor:
					embed.description += f"{rows[0]}\n"

				await interaction.response.edit_message(embed=embed, view=self)


class TagCog(app_commands.Group, name="tag"):
	def __init__(self, client):
		self.client = client
		self.permissioncheck = permissonschecker.PermissionsChecker(client)
		super().__init__()


	async def check_in_db(self, row_name, guild_id:int):
		async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name = ?", (guild_id, row_name)) as cursor:
			row = await cursor.fetchone()

		return False if not row else True


	async def check_author_in_db(self, author_id:int, row_name, guild_id:int):
		async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name = ? AND user_id = ?", (guild_id, row_name, author_id)) as cursor:
			row = await cursor.fetchone()

		return False if not row else True


	async def update_use(self, row_name, guild_id:int):
		await self.client.db.execute("UPDATE database SET tag_use = tag_use + 1 WHERE guild_id = ? AND tag_name = ?", (guild_id, row_name))
		await self.client.db.commit()


	async def get_stats(self, guild_id:int, author_id:int):
		async with self.client.db.execute("SELECT COUNT(tag_name) FROM database WHERE guild_id = ? AND user_id = ?", (guild_id, author_id)) as cursor:
			tag_total_name = await cursor.fetchone()

		tag_total_use = 0

		async with self.client.db.execute("SELECT tag_use FROM database WHERE guild_id = ? AND user_id = ?", (guild_id, author_id)) as cursor:
			async for uses in cursor:
				tag_total_use = tag_total_use + uses[0]

		return tag_total_name[0], tag_total_use


	@app_commands.command(name="help", description="Список команд")
	async def help(self, interaction:discord.Interaction):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			embed=discord.Embed(title='Список команд',description="", colour=discord.Colour.default())
			embed.add_field(name="`/tag add`", value="Создание тега", inline=False)
			embed.add_field(name="`/tag remove`", value="Удаление тега", inline=False)
			embed.add_field(name="`/tag edit`", value="Редактирование тега", inline=False)
			embed.add_field(name="`/tag call`", value="Вызов тега", inline=False)
			embed.add_field(name="`/tag random`", value="Вызов случайного тега", inline=False)
			embed.add_field(name="`/tag info`", value="Информация о теге", inline=False)
			embed.add_field(name="`/tag stats`", value="Статистика пользователя", inline=False)
			embed.add_field(name="`/tag search`", value="Поиск тега по имени (100 тегов)", inline=False)
			embed.add_field(name="`/tag delete`", value="Удаление тега (доступно Администратору)", inline=False)
			embed.set_footer(text="Версия: 2.1.0\nАвтор: Ykpauneu#1625")
			await interaction.followup.send(embed=embed)

		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="add", description="Создание тега")
	@app_commands.describe(name="Имя тега")
	async def tagadd(self, interaction:discord.Interaction, name:str):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			check = await self.check_in_db(name, interaction.guild.id)

			if not check:
				await interaction.followup.send(f"{interaction.user.mention}, теперь напишите текст для тега!")
				while True:
					try:
						message = await self.client.wait_for("message", check=lambda message: message.author == interaction.user and interaction.channel == message.channel, timeout=30.0)
						if message.attachments:
							message.content = message.attachments[0].url

						if len(message.content) > 2000:
							await interaction.followup.send(f"{interaction.user.mention}, укажите меньше 2000 символов!")
							return
						
						await self.client.db.execute("INSERT INTO database (guild_id, user_id, tag_name, tag_text, tag_use) VALUES (?,?,?,?,?)", (interaction.guild.id, interaction.user.id, name, message.content, 0))
						await interaction.followup.send(f"{interaction.user.mention}, тег **{name}** был успешно создан!")		
						return

					except asyncio.TimeoutError:
						await interaction.followup.send(f"{interaction.user.mention}, время вышло!")
						return
			else:
				await interaction.followup.send(f"{interaction.user.mention}, тег с таким именем уже есть!")
				return
		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="remove", description="Удаление тега")
	@app_commands.describe(name="Имя тега")
	async def tagremove(self, interaction:discord.Interaction, name:str):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			check = await self.check_author_in_db(interaction.user.id, name, interaction.guild.id)

			if check:
				await self.client.db.execute("DELETE FROM database WHERE guild_id = ? AND tag_name = ? AND user_id = ?", (interaction.guild.id, name, interaction.user.id))
				await self.client.db.commit()
				await interaction.followup.send(f"{interaction.user.mention}, тег **{name}** был успешно удалён!")

			else:
				await interaction.followup.send(f"{interaction.user.mention}, у вас нет такого тега!")
				return
		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="edit", description="Редактирование тега")
	@app_commands.describe(name="Имя тега")
	async def tagedit(self, interaction:discord.Interaction, name:str):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			check = await self.check_author_in_db(interaction.user.id, name, interaction.guild.id)

			if check:
				await interaction.followup.send(f"{interaction.user.mention}, теперь напишите новый текст для тега!")
				while True:
					try:
						message = await self.client.wait_for("message", check=lambda message: message.author == interaction.user and interaction.channel == message.channel, timeout=300.0)

						if len(message.content) > 2000:
							await interaction.followup.send(f"{interaction.user.mention}, укажите меньше 2000 символов!")
							return
					
						else:
							await self.client.db.execute("UPDATE database SET tag_text == ? WHERE guild_id = ? AND tag_name = ? AND user_id = ?", (message.content, interaction.guild.id, name, interaction.user.id))
							await self.client.db.commit()
							await interaction.followup.send(f"{interaction.user.mention}, тег **{name}** был успешно редактирован!")
							return

					except asyncio.TimeoutError:
						await interaction.followup.send(f"{interaction.user.mention}, время вышло!")
						return

			else:
				await interaction.followup.send(f"{interaction.user.mention}, у вас нет такого тега!")
				return
		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="call", description="Вызов тега")
	@app_commands.describe(name="Имя тега")
	async def tagcall(self, interaction:discord.Interaction, name:str):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			check = await self.check_in_db(name, interaction.guild.id)

			if check:
				await self.update_use(name, interaction.guild.id)
				async with self.client.db.execute("SELECT tag_text FROM database WHERE guild_id = ? AND tag_name = ?", (interaction.guild.id, name)) as cursor:
					tag_text = await cursor.fetchone()
		
				await interaction.followup.send(tag_text[0])

			else:
				possible = []
				async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name LIKE ? OR tag_name LIKE ? ORDER BY tag_use LIMIT ?", (interaction.guild.id, '%'+name+'%', name, 3)) as cursor:
					async for rows in cursor:
						possible.append(rows[0])

				possible_str = str(possible).strip('[]')

				await interaction.followup.send(f"{interaction.user.mention}, такого тега нет!\nВозможно, Вы имели в виду: {possible_str}")

		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="random", description="Вызов случайного тега")
	async def tagrandom(self, interaction:discord.Interaction):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			tags = []
			async with self.client.db.execute("SELECT tag_name, tag_text FROM database WHERE guild_id = ?", (interaction.guild.id, )) as cursor:
				async for rows in cursor:
					if rows:
						tags.append(rows)
					
					else:
						await interaction.followup.send(f"{interaction.user.mention}, на сервере нет тегов!")
						return									

				tag_result = random.choice(tags)
				try:
					await self.update_use(tag_result[0], interaction.guild.id)
					await interaction.followup.send(f"Тег: **{tag_result[0]}**\n{tag_result[1]}")
				
				except:
					await interaction.followup.send(f"{interaction.user.mention}, на сервере нет тегов!")
					return			

		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="info", description="Информация о теге")
	@app_commands.describe(name="Имя тега")
	async def taginfo(self, interaction:discord.Interaction, name:str):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			check = await self.check_in_db(name, interaction.guild.id)

			if check:
				async with self.client.db.execute("SELECT user_id, tag_use FROM database WHERE guild_id = ? AND tag_name = ?", (interaction.guild.id, name)) as cursor:
					tag_info = await cursor.fetchone()

				owner = interaction.guild.get_member(tag_info[0])

				embed=discord.Embed(title=name,description="", colour=discord.Colour.default())
				embed.add_field(name="Создатель:", value=owner.mention, inline=True)
				embed.add_field(name="Использований:", value=tag_info[1], inline=True)
				await interaction.followup.send(embed=embed)

			else:
				await interaction.followup.send(f"{interaction.user.mention}, такого тега нет!")
				return
		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="stats", description="Статистика пользователя")
	@app_commands.describe(member="Пользователь")
	async def tagstats(self, interaction:discord.Interaction, member:discord.Member=None):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			if member is None:
				member = interaction.user 

			name, use = await self.get_stats(interaction.guild.id, member.id)

			embed=discord.Embed(title=f"{member.name}#{member.discriminator}", colour=discord.Colour.default())
			embed.add_field(name="Кол-во тегов:", value=name, inline=True)
			embed.add_field(name="Кол-во использований:", value=use, inline=True)
			await interaction.followup.send(embed=embed)

		else:
			await interaction.followup.send("Команды доступны только на сервере!")


	@app_commands.command(name="search", description="Поиск тега по имени (100 тегов)")
	@app_commands.describe(name="Имя тега")
	async def tagsearch(self, interaction:discord.Interaction, name:str):
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			view = Search(self.client, interaction.user.id, name)
			embed=discord.Embed(title=f'Поиск **{name}** (1/10)',description="", colour=discord.Colour.default())
			async with self.client.db.execute("SELECT tag_name FROM database WHERE guild_id = ? AND tag_name LIKE ? OR tag_name LIKE ? ORDER BY tag_use DESC LIMIT ? OFFSET ?", (interaction.guild.id, '%'+name+'%', name, 10, 0)) as cursor:
				async for rows in cursor:
					embed.description += f"{rows[0]}\n"

				await interaction.response.send_message(embed=embed, view=view)
		else:
			await interaction.response.send_message("Команды доступны только на сервере!")


	@app_commands.command(name="delete", description="Удаление тега (доступно Администратору)")
	@app_commands.describe(name="Имя тега")
	@commands.has_permissions(administrator=True)
	async def tagdelete(self, interaction:discord.Interaction, name:str):
		await interaction.response.defer(thinking=True)
		is_guild = await self.permissioncheck.is_guild(interaction)
		if is_guild:
			check = await self.check_in_db(name, interaction.guild.id)

			if check:
				await self.client.db.execute("DELETE FROM database WHERE guild_id = ? AND tag_name = ?", (interaction.guild.id, name))
				await self.client.db.commit()
				await interaction.followup.send(f"{interaction.user.mention}, тег **{name}** был успешно удалён!")

			else:
				await interaction.followup.send(f"{interaction.user.mention}, такого тега нет!")
				return
		else:
			await interaction.followup.send("Команды доступны только на сервере!")


async def setup(client):
	client.tree.add_command(TagCog(client))