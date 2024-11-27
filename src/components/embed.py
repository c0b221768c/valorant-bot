from datetime import datetime

from discord import Embed


class EmbedFactory:
    def __init__(self, cache_data):
        self.headcount = cache_data["headcount"]
        self.participants = list(cache_data["participants"])
        self.non_participants = list(cache_data["non_participants"])
        self.unix = int(cache_data["date"].timestamp())
        self.slot = max(0, int(self.headcount) - len(self.participants))

    def build(self) -> Embed:
        embed = Embed(color=0xA9CEEC)

        embed.title = f"✨ {self.get_title()} ✨"

        # 開始時間フィールド
        embed.add_field(
            name=f"⏰ 開始予定時間 ⏰",
            value=f"<t:{self.unix}:f>",
            inline=False,
        )

        # 参加者一覧
        embed.add_field(
            name="参加者一覧",
            value="\n".join(f"<@{p}>" for p in self.participants) or "なし",
            inline=True,
        )
        embed.add_field(
            name="不参加者一覧",
            value="\n".join(f"<@{p}>" for p in self.non_participants) or "なし",
            inline=True,
        )
        embed.set_footer(text=f"残り参加枠: {self.slot}人")


        return embed

    def get_title(self) -> str:
        titles = {
            2: "VALORANT デュオ募集",
            3: "VALORANT トリオ募集",
            5: "VALORANT フルパ募集",
            10: "VALORANT カスタム募集",
        }
        return titles.get(self.headcount, "VALORANT 募集")
