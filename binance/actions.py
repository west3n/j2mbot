import ccxt
import decouple

from database import binance_db


async def get_balance(tg_id):
    binance_keys = await binance_db.get_binance_keys(tg_id)
    api_key = binance_keys[0]
    api_secret = binance_keys[1]
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret
    })
    balances = exchange.fetch_balance()
    for currency, balance in balances['total'].items():
        if currency == 'USDT':
            return balance


def check_credentials(api_key, api_secret):
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret
    })
    try:
        exchange.fetch_balance()
        return True
    except ccxt.AuthenticationError:
        return False
