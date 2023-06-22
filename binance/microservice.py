import requests
import secrets
from eth_account import Account


async def create_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return private_key, acct.address


async def microservice_(tg_id, invitor):
    private_key, address = await create_wallet()
    url = 'http://109.172.81.133:3000/'
    body = {
        "address": address,
        "id": int(tg_id),
        "inviterId": int(invitor),
    }

    response = requests.post(url, json=body)

    if response.status_code == 200:
        response_data = response.json()
        return response_data, private_key, address
    else:
        return None
    