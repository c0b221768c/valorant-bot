import discord
from discord.ext import commands

from cache.cache_manager import CacheManager
from cache.member_cache import MemberCache
from components.embed import EmbedFactory
from components.views import RecruitmentView
from config.settings import settings
from utils.helpers import generate_uuid
from utils.validator import DateValidator, HeadcountValidator, ParticipantsValidator

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
member_cache = MemberCache()


@bot.event
async def on_ready():
    await bot.tree.sync()
    for guild in bot.guilds:
        member_cache.load_memebers(guild)
    print(f"Bot is ready. Logged in as {bot.user}")


@bot.event
async def on_member_join(member):
    member_cache.update_member(member.guild.id, member)


@bot.event
async def on_member_remove(member):
    member_cache.remove_member(member.guild.id, member.id)


@bot.tree.command(
    name="joinus",
    description="Valorantのメンバー募集を行います。引数は任意で指定できます。",
)
@discord.app_commands.describe(
    headcount="募集人数を指定できます (2, 3, 5, 10)",
    participants="参加者をメンションで指定できます（半角スペース区切り）",
    date="日付を指定できます（HH:MM, MM/DD HH:MM, YYYY/MM/DD HH:MM, または NN 分後）",
)
async def joinus(
    interaction: discord.Interaction,
    headcount: int = None,
    participants: str = None,
    date: str = None,
):
    try:
        # バリデーション
        headcount = HeadcountValidator(headcount).validate()
        participants = set(
            await ParticipantsValidator(participants, interaction).validate()
        )
        date = DateValidator(date).validate()

        # キャッシュ作成
        recruitment_id = generate_uuid()
        cache_manager = CacheManager()
        cache_manager.create_recruitment(recruitment_id, headcount, participants, date)

        # EmbedとView作成
        embed = EmbedFactory(cache_manager.get_recruitment_data(recruitment_id)).build()
        view = RecruitmentView(cache_manager, recruitment_id)

        await interaction.response.send_message(embed=embed, view=view)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)


bot.run(settings.DISCORD_TOKEN)
