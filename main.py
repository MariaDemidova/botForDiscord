import os
import disnake
from disnake.ext import commands
from configparser import ConfigParser
import aiosqlite

config  = ConfigParser()
config.read('config.ini',  encoding= 'utf-8')

BOT_TOKEN = config['API']['BOT_TOKEN']
class HerBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=disnake.Intents.all(),
            help_command=None,
        )
        self.lvl_ranks = config['RANKS']
        self.system_channel = int(config['SETTINGS']['SYSTEM_CHANNEL'])
    async def check_level(self, user_id, user_name, add_exp):
        db = await aiosqlite.connect('users.db')
        channel = self.get_channel(self.system_channel)
        cursor = await db.execute(f'SELECT exp, lvl FROM users WHERE id = {user_id}')
        data = await cursor.fetchone()
        current_exp = data[0]
        current_lvl = data[1]
        user_nick = bot.get_user(user_id).display_name
        if (current_exp + add_exp) >= (2**current_lvl)*100:
            current_exp = current_exp + add_exp - (2**current_lvl)*100
            current_lvl += 1
            while current_exp >= (2**current_lvl)*100:
                current_exp -= (2**current_lvl)*100
                current_lvl += 1
            await channel.send(f"{user_nick}! Ты достиг(ла) уровня {current_lvl}. " +
                                f"Теперь ты {self.lvl_ranks[str(current_lvl)]}!\n Трудись усерднее и будешь вознагражден(а)! (Нет)")

        elif (current_exp + add_exp) < 0:
            current_exp =(2**(current_lvl-1))*100 + current_exp + add_exp
            current_lvl -= 1
            while (current_exp < 0):
                current_exp = (2**(current_lvl-1))*100 + current_exp
                current_lvl -= 1
                if current_lvl == 0:
                    current_exp = 0
            await channel.send(f' {user_nick}! Ты достиг(ла) дна. Теперь твой уровень {current_lvl}. Теперь ты {self.lvl_ranks[str(current_lvl)]}!\nПознай боль, жалкий людишка ☠️!')
        else:
            current_exp += add_exp
        await db.execute(f'UPDATE users SET exp = {current_exp}, lvl = {current_lvl} WHERE id = {user_id}')
        await db.commit()
        await cursor.close()
        await db.close()
    def parse_int_tuple(self, input):
        return tuple(int(k.strip()) for k in input[1:-1].split(','))

    def parse_str_tuple(self, input):
        return tuple((k.strip()) for k in input[1:-1].split(','))

if __name__ == "__main__":
    bot = HerBot()
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")


    bot.run(BOT_TOKEN)
