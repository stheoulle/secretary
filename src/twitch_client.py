import asyncio
from twitchio.ext import commands

from .rag import RAGEngine
from .config import TwitchConfig


class TwitchRagBot(commands.Bot):
    def __init__(self, twitch_cfg: TwitchConfig, rag: RAGEngine):
        super().__init__(
            token=twitch_cfg.token,
            client_id=twitch_cfg.client_id,
            client_secret=twitch_cfg.client_secret,
            bot_id=twitch_cfg.bot_id,
            prefix=twitch_cfg.prefix,
            initial_channels=twitch_cfg.channels,
        )
        self.twitch_cfg = twitch_cfg
        self.rag = rag

    async def event_ready(self):
        print(f"Logged in as {self.twitch_cfg.nick}. Connected to {self.twitch_cfg.channels}.")

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name="ask")
    async def ask(self, ctx: commands.Context, *, question: str):
        await ctx.send("Thinking...")
        answer = await asyncio.to_thread(self.rag.query, question)
        await ctx.send(answer[:450])
