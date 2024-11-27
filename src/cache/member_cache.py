class MemberCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cache = {}
        return cls._instance

    def load_memebers(self, guild):
        """ログイン時にメンバー情報をキャッシュに保存する"""
        self.cache[guild.id] = {
            member.id: {
                "name": f"{member.name}#{member.discriminator}",
                "is_bot": member.bot,
            }
            for member in guild.members
        }
    
    def get_member(self, guild_id, member_id):
        """ギルドIDとメンバーIDからメンバー情報を取得する"""
        return self.cache.get(guild_id, {}).get(member_id)
    
    def update_member(self, guild_id, member):
        """メンバー情報を更新する"""
        if guild_id not in self.cache:
            self.cache[guild_id] = {}
        self.cache[guild_id][member.id] = {
            "name" : f"{member.name}#{member.discriminator}",
            "is_bot": member.bot,
        }

    def remove_member(self, guild_id, member_id):
        """メンバー情報を削除する"""
        if guild_id in self.cache:
            self.cache[guild_id].pop(member_id, None)