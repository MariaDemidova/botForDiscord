from disnake.ext import commands
import disnake
import aiosqlite
from configparser import ConfigParser

config  = ConfigParser()
config.read('config.ini',  encoding= 'utf-8')

class EventListeners(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.exp_stop_list = self.bot.parse_int_tuple(config['SETTINGS']['BOTS_LIST'])
        self.admin_roles_list = self.bot.parse_int_tuple(config['SETTINGS']['ADMIN_ROLE_IDS'])
        self.system_channel = int(config['SETTINGS']['SYSTEM_CHANNEL'])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = await aiosqlite.connect('users.db')
        # channel = member.guild.system_channel
        channel = self.bot.get_channel(self.system_channel)
        if await db.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
            await db.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0,0,0)")
            await db.commit()
            await db.close()
        else:
            pass     
        embed = disnake.Embed( title="Свежая кровь!", description=f'{member.name}#{member.discriminator}', color = 'red')
        await channel.send(embed)

    @commands.Cog.listener()
    async def on_message(self,message):

        if message.author.id not in self.exp_stop_list:
            content_len = len(message.content.split())
            if content_len > 5:
                content_len = 5
            await self.bot.check_level(user_id=message.author.id, user_name = message.author.name, add_exp=content_len)

    @commands.Cog.listener()
    async def on_ready(self):
        db = await aiosqlite.connect('users.db')
        cursor = await db.execute(
                """
                    CREATE TABLE IF NOT EXISTS users (
                    name TEXT,
                    id INT,
                    exp INT,
                    lvl INT,
                    voice_time INT,
                    enter_voice INT
                    )
                """
                )
        await db.commit()

        for guild in self.bot.guilds:
            for member in guild.members:
                cursor = await db.execute(f"SELECT id FROM users WHERE id = {member.id}") 
                check = await cursor.fetchone()
                if check is None:
                    await db.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, 0)")
                else:
                    pass
        await db.commit()
        await cursor.close()
        await db.close()

        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})\n------")

def setup(bot) -> None:
    bot.add_cog(EventListeners(bot))