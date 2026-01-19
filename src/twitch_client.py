import asyncio
from twitchio.ext import commands

from .rag import RAGEngine
from .config import TwitchConfig


class TwitchRagBot(commands.Bot):
    def __init__(self, twitch_cfg: TwitchConfig, rag: RAGEngine):
        super().__init__(
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
        print("Bot is ready and listening for messages.")

    async def event_message(self, message):
        print("MESSAGE RECEIVED:", message.content)
        if message.echo:
            return

        content = message.content.strip()

        # 🔍 If message contains a question mark, trigger RAG
        if "?" in content:
            print(f"RAG Triggered by: {content}")

            # Optional: basic anti-spam filter
            if len(content) < 5:
                return

            await message.channel.send("Thinking...")

            try:
                answer = await asyncio.to_thread(self.rag.query, content)

                # Twitch message limit ≈ 500 chars
                await message.channel.send(answer[:450])

            except Exception as e:
                print("RAG error:", e)
                await message.channel.send("Error while processing the question.")

        # Keep command handling if you want both modes
        await self.handle_commands(message)

    @commands.command(name="ask")
    async def ask(self, ctx: commands.Context, *, question: str):
        await ctx.send("Thinking...")
        answer = await asyncio.to_thread(self.rag.query, question)
        await ctx.send(answer[:450])
