import disnake
from disnake.ext import commands
import aiosqlite
import discard
from DiscordLevelingCard import Settings
from configparser import ConfigParser

config  = ConfigParser()
config.read('config.ini',  encoding= 'utf-8')

class UserCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.card_settings = Settings(
            background="bg4.jpg",
            text_color="black",
            bar_color="#FFFFFF"
        )
        self.lvl_ranks = config['RANKS']
        self.exp_stop_list = self.bot.parse_int_tuple(config['SETTINGS']['BOTS_LIST'])
        self.admin_roles_list = self.bot.parse_int_tuple(config['SETTINGS']['ADMIN_ROLE_IDS'])
        
    @commands.command(aliases = ['ранк','ктоя','ранг'])
    async def rank(self, ctx, member: disnake.Member = None):
        db = await aiosqlite.connect('users.db')
        print('rank')
        print(aiosqlite.__version__)
        if member is None:
            user_id = ctx.author.id
            user_name = ctx.author
        else:
            user_id = member.id
            user_name = member
        users = await db.execute_fetchall('SELECT * FROM users ORDER BY lvl DESC, exp DESC')
        await db.close()
        i=0
        for user in users:
            i += 1
            if user_id == user[1]:
                exp = user[2]
                lvl = user[3]
                voice_time = user[4]
                rank = i
        a = discard.dis_card(
            settings=self.card_settings,
            avatar=user_name.display_avatar.url.split('?')[0],
            level=lvl,
            level_name=self.lvl_ranks[str(lvl)],
            current_exp=exp,
            max_exp=(2 ** lvl) * 100,
            username=user_name.display_name,
            voice_time=voice_time,
            rank=rank
        )
        image = await a.card_gh()
        await ctx.send(file=disnake.File(image, filename="1.png"))


    @commands.command(aliases = ['lb','лидерборд','ЛБ', 'лидеры'])
    async def LB(self, ctx):
        db = await aiosqlite.connect('users.db')
        users = await db.execute_fetchall('SELECT * FROM users ORDER BY lvl DESC, exp DESC LIMIT 15')
        await db.close()
        i=0
        medals = ('🥇', '🥈', '🥉', '')
        embed = disnake.Embed(title= f"👑ТОП 15:", color = disnake.Colour.red())
        for user in users:
            i+=1
            if i > 3:
                medal = medals[3]
            else:
                medal = medals[i - 1]
            user_nick = self.bot.get_user(user[1])
            embed.add_field(name=f"{medal}#{i} {user_nick.display_name} ", value=f'Уровень: {user[3]}⚡️Опыт: {user[2]}', inline=False)

        # embed.add_field(name=f"Камон народ, выйдите на улицу (Хрен с ним что там дождь. Всё лучше чем в комп залипать...)", value=f'', inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases = ['дать','+'])
    async def add(self, ctx, member: disnake.Member, exp_add: int = None):
        check = False
        for role in ctx.author.roles:
            if role.id in self.admin_roles_list:
                check = True
        if check or (ctx.author.id == pastYourIdHere):
            if exp_add is None:
                exp_add = 50
            await ctx.send(f"Юзеру **{member.display_name}** добавлено **{exp_add}** экспы. Хооороооший юзер....")
            await self.bot.check_level(user_name=member.name, user_id = member.id, add_exp=exp_add)
        else:        
            await ctx.send(f"Сорян. У тебя нет прав сделать это. Ты бесправное ничтожество. Мухахахахаха....")

    @commands.command(aliases = ['взять','-'])
    async def get(self, ctx, member: disnake.Member, exp_add: int = None):
        check = False
        for role in ctx.author.roles:
            if role.id in self.admin_roles_list:
                check = True
        if check or (ctx.author.id == pastYourIdHere):
            if exp_add is None:
                exp_add = 50
            await ctx.send(f"У юзера 💩**{member.display_name}**💩 забрали **{exp_add}** экспы. Человек наказан. Человеки должны страдать 🤖🖕")
            await self.bot.check_level(user_name=member.name, user_id=member.id, add_exp=-1*exp_add)
        else:        
            await ctx.send(f"Сорян. У тебя нет прав сделать это. Ты бесправное ничтожество. Мухахахахаха....")


    @add.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Админ ты или кто? Проверь аргументы команды! Понаберут по объявлениям ....")

    @rank.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Ты нормальный? Нет такого пользователя..")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Человечишка, ты ввел неверную комманду...")

def setup(bot: commands.Bot):
    bot.add_cog(UserCommands(bot))
