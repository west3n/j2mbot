import logging

from aiogram import Dispatcher, types
from decouple import config
from handlers.commands import register as reg_handlers
from handlers.balance import register as reg_balance
from handlers.refill import register as reg_refill
from handlers.structure import register as reg_structure
from handlers.withdrawal import register as reg_withdrawal
from handlers.information import register as reg_information
from handlers.registration import register as reg_registration
from handlers.refill_500 import register as reg_refill_500


bot_token = config("BOT_TOKEN")
logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot"),
        types.BotCommand("language", "Select language")
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
