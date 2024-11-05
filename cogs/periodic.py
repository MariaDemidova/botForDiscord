from disnake.ext import commands, tasks
import time
import aiosqlite
from configparser import ConfigParser


config  = ConfigParser()
config.read('config.ini',  encoding= 'utf-8')


class Periodic(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.system_channel = int(config['SETTINGS']['SYSTEM_CHANNEL'])
        self.no_voice_exp_list = self.bot.parse_int_tuple(config['SETTINGS']['NO_VOICE_EXP_LIST'])

    def cog_unload(self):
        self.periodic_check_voice.cancel()

    @tasks.loop(seconds=30.0) #Проверяет в базе у юзеров время в голосе и преобразует в опыт
    async def periodic_check_voice(self):
        db = await aiosqlite.connect('users.db')
        data = await db.execute_fetchall('SELECT * FROM users WHERE enter_voice > 0')
        for i in data:
            add_exp = int((time.time() - i[5])/10)
            await self.bot.check_level(user_id=i[1], user_name = i[0], add_exp=add_exp)
            await db.execute(f'UPDATE users SET enter_voice = {int(time.time())}, voice_time = voice_time + {add_exp*10} WHERE id = {i[1]}')
            await db.commit()
            # print(f'add {i[4]} to {i[0]}')
        await db.close()

    @periodic_check_voice.before_loop
    async def before_periodic_check_voice(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        db = await aiosqlite.connect('users.db')
        if (before.channel is None) and (after.channel is not None and after.channel.id not in self.no_voice_exp_list):
            #Зашел
            await db.execute(f'UPDATE users SET enter_voice = {int(time.time())} WHERE id = {member.id}')
            print(f'Enter user {member.name} Channel = {after.channel.id}')
        elif before.channel is not None and after.channel is None:
            if before.channel.id not in self.no_voice_exp_list:
                await self.exit_voice(member=member)
                print(f'Exit user {member.name}')
        elif before.channel is not None and after.channel is not None:
            if after.channel.id in self.no_voice_exp_list:
                await self.exit_voice(member=member)
                print(f'Exit user {member.name}')
            if before.channel.id in self.no_voice_exp_list:
                await db.execute(f'UPDATE users SET enter_voice = {int(time.time())} WHERE id = {member.id}')
                print(f'Enter user {member.name} Channel = {after.channel.id}')
        await db.commit()
        await db.close()
    @staticmethod
    async def exit_voice(member):
        db = await aiosqlite.connect('users.db')
        cursor = await db.execute(f'SELECT enter_voice FROM users WHERE id = {member.id}')
        enter_voice = await cursor.fetchone()
        if int(enter_voice[0]) > 0:
            add_voice_time = int(time.time() - enter_voice[0])
            await db.execute(
                f'UPDATE users SET voice_time = voice_time + {add_voice_time}, enter_voice = 0 WHERE id = {member.id}')
            await db.commit()
            await cursor.close()
            await db.close()

    @commands.Cog.listener()
    async def on_ready(self):
        self.periodic_check_voice.start()

def setup(bot: commands.Bot):
    bot.add_cog(Periodic(bot))

