import re
from datetime import datetime, timedelta

from cache.member_cache import MemberCache


def is_valid_time(hour: int, minute: int) -> bool:
    return 0 <= hour <= 23 and 0 <= minute <= 59


def is_valid_date(year: int, month: int, day: int) -> bool:
    try:
        datetime(year, month, day)
        return True
    except ValueError:
        return False


class HeadcountValidator:
    def __init__(self, headcount: int):
        self.headcount = headcount if headcount else 5

    def validate(self) -> int:
        if self.headcount not in (2, 3, 5, 10):
            raise ValueError("募集人数は 2, 3, 5, 10 のいずれかにしてください。")
        return self.headcount


class ParticipantsValidator:
    def __init__(self, participants: str, interaction):
        self.interaction = interaction
        self.guild = interaction.guild
        self.participants = participants.split() if participants else []
        self.cache = MemberCache()

    async def validate(self) -> list[int]:
        """
        ユーザーが指定した参加者をキャッシュで検証します。
        """
        member_ids = [self.interaction.user.id]  # コマンド実行者を含める

        for mention in self.participants:
            # メンションのID部分を直接抽出
            user_id = int(mention.strip("<@!>"))

            # キャッシュからユーザー情報を取得
            member = self.cache.get_member(self.guild.id, user_id)
            if member and not member["is_bot"]:
                member_ids.append(user_id)
            else:
                raise ValueError(
                    f"指定されたユーザーが存在しないか、Botです: {mention}"
                )

        return member_ids


class DateValidator:
    def __init__(self, date_str: str = None):
        self.date_str = date_str

    def validate(self) -> datetime:
        now = datetime.now()

        if not self.date_str:
            return now + timedelta(minutes=30)

        patterns = [
            (r"^(\d{1,2}):(\d{1,2})$", self.parse_time_only),
            (r"^(\d{1,2})/(\d{1,2}) (\d{1,2}):(\d{1,2})$", self.parse_date_time),
            (
                r"^(\d{4})/(\d{1,2})/(\d{1,2}) (\d{1,2}):(\d{1,2})$",
                self.parse_full_date,
            ),
            (r"^\d+$", self.parse_minutes_later),
        ]

        for pattern, parser in patterns:
            if match := re.match(pattern, self.date_str):
                return parser(match).astimezone()

        raise ValueError(
            "入力形式が不正です。許可されている形式は 'HH:MM', 'MM/DD HH:MM', 'YYYY/MM/DD HH:MM', 'NN (分後)' です。"
        )

    def parse_time_only(self, match) -> datetime:
        now = datetime.now()
        hour, minute = int(match.group(1)), int(match.group(2))
        if is_valid_time(hour, minute):
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        raise ValueError("無効な時間指定です。")

    def parse_date_time(self, match) -> datetime:
        now = datetime.now()
        month, day, hour, minute = map(int, match.groups())
        if is_valid_date(now.year, month, day) and is_valid_time(hour, minute):
            return datetime(now.year, month, day, hour, minute)
        raise ValueError("無効な日付または時間です。")

    def parse_full_date(self, match) -> datetime:
        year, month, day, hour, minute = map(int, match.groups())
        if is_valid_date(year, month, day) and is_valid_time(hour, minute):
            return datetime(year, month, day, hour, minute)
        raise ValueError("無効な日付です。")

    def parse_minutes_later(self, match) -> datetime:
        minutes = int(match.group(0))
        if minutes > 0:
            return datetime.now() + timedelta(minutes=minutes)
        raise ValueError("分後の指定は正の整数でなければなりません。")
