import asyncio

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
    usdt_balance = balances['total']['USDT']
    busd_balance = balances['total']['BUSD']
    return usdt_balance, busd_balance


async def get_balance_j2m():
    all_keys = await binance_db.get_api_keys()
    usdt_balance = 0
    busd_balance = 0
    for keys in all_keys:
        api_key, api_secret = keys
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret
        })
        try:
            balances = exchange.fetch_balance(params={'type': 'future'})
            usdt_balance += float(balances['total']['USDT'])
            busd_balance += float(balances['total']['BUSD'])
        except ccxt.errors.AuthenticationError:
            pass
    return usdt_balance, busd_balance


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
