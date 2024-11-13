import asyncio
import logging
import sys
from contextlib import suppress

import aiogram
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.bot import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import scheduler

import stars

API_TOKEN = '7602273048:AAGsdgh0cZukQWalZuhitZKlwCawAiTV4pQ'

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main() -> None:
    # storage = RedisStorage.from_url('redis://localhost:6379/0')

    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    async_scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    async_scheduler.start()
    
    async_scheduler.add_job(func=scheduler.check_active_lottery, kwargs={"bot": bot}, trigger=CronTrigger.from_crontab('*/1 * * * *')) # 0 * * * *
    
    dp.include_routers(stars.router, scheduler.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())