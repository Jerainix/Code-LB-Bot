from os import environ

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.types import ParseMode
from dotenv import load_dotenv
from loguru import logger

from handlers import RegistrationHandlers, EventsHandlers, DialogHandlers
from services.db import DB

db = DB()


async def __on_start_up(_dp: Dispatcher) -> None:
    DialogHandlers(_dp)
    RegistrationHandlers(_dp)
    EventsHandlers(_dp)
    logger.info(f'Bots starts')


if __name__ == '__main__':
    load_dotenv()

    storage = MongoStorage(uri=environ['DB-LINK'], db_name='randprog')
    bot = Bot(token=environ['TOKEN'], parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher(bot, storage=storage)
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
