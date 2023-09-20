import logging

from aiogram import Dispatcher, types
from decouple import config

from demo.dm_balance import register as reg_demo_balance
from demo.dm_commands import register as reg_demo_commands
from demo.dm_refill import register as reg_demo_refill
from demo.dm_refill_500 import register as reg_demo_refill_500
from demo.dm_refill_stabpool import register as reg_stabpool_dm
from handlers.autoposting import register as reg_autoposting
from handlers.balance import register as reg_balance
from handlers.commands import register as reg_handlers
from handlers.information import register as reg_information
from handlers.refill import register as reg_refill
from handlers.refill_500 import register as reg_refill_500
from handlers.refill_stabpool import register as reg_stabpool
from handlers.registration import register as reg_registration
from handlers.structure import register as reg_structure
from handlers.withdrawal import register as reg_withdrawal

bot_token = config("BOT_TOKEN")
logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Main Menu / Главное меню"),
        types.BotCommand("language", "Select language / Выбрать язык")
    ])


def register_handlers(dp: Dispatcher):
    reg_handlers(dp)
    reg_balance(dp)
    reg_refill(dp)
    reg_structure(dp)
    reg_withdrawal(dp)
    reg_information(dp)
    reg_registration(dp)
    reg_refill_500(dp)
    reg_stabpool(dp)
    reg_stabpool_dm(dp)
    reg_autoposting(dp)
    reg_demo_commands(dp)
    reg_demo_balance(dp)
    reg_demo_refill(dp)
    reg_demo_refill_500(dp)
    