import logging
import asyncio
import aiohttp

class DiscordLogHandler(logging.Handler):
    def __init__(self, webhook_url, level=logging.INFO):
        super().__init__(level)
        self.webhook_url = webhook_url
        self.queue = asyncio.Queue()

    async def start(self):
        asyncio.create_task(self._worker())

    async def _worker(self):
        async with aiohttp.ClientSession() as session:
            while True:
                message = await self.queue.get()
                if len(message) > 2000:
                    message = message[-1997:] + "..."
                try:
                    await session.post(self.webhook_url, json={"content": f"{message}"})
                except Exception as e:
                    print("Logging to Discord failed:", e)

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.queue.put_nowait(log_entry)
        except asyncio.QueueFull:
            print("Log queue full, skipping log.")
