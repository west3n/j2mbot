import base64
import hashlib
import hmac
import json
import time
import decouple
import requests

api_key = decouple.config("THEDEX_API")
secret_key = decouple.config("THEDEX_SECRET")
baseUrl = 'https://app.thedex.cloud'
nonce = time.time_ns() // 1_000_000


async def create_invoice(amount, tg_id, title):
    request = '/api/v1/invoices/create'

    data = {
        'request': request,
        'nonce': nonce,
        'amount': amount,
        'clientId': f"{tg_id}",
        'currency': 'USD',
        'merchantId': decouple.config("THEDEX_MERCHANT_ID"),
        'title': f"{title}"
    }

    completeUrl = baseUrl + request
    data_json = json.dumps(data, separators=(',', ':'))
    payload = base64.b64encode(data_json.encode('ascii'))
    signature = hmac.new(secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()

    headers = {
        'Content-type': 'application/json',
        'X-EX-APIKEY': api_key,
        'X-EX-PAYLOAD': payload,
        'X-EX-SIGNATURE': signature
    }

    resp = requests.post(completeUrl, headers=headers, data=data_json)
    resp_json = json.dumps(resp.json(), sort_keys=True, indent=4)
    print(resp)
    return json.loads(resp_json)['invoiceId']


async def pay_invoice(currency, invoice_id):
    request = '/api/v1/invoices/currency'

    data = {
        "invoiceId": invoice_id,
        'nonce': nonce,
        "payCurrency": currency,
        'request': request,

    }
    completeUrl = baseUrl + request
    data_json = json.dumps(data, separators=(',', ':'))
    payload = base64.b64encode(data_json.encode('ascii'))
    signature = hmac.new(secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()

    headers = {
        'Content-type': 'application/json',
        'X-EX-APIKEY': api_key,
        'X-EX-PAYLOAD': payload,
        'X-EX-SIGNATURE': signature,
    }
    resp = requests.post(completeUrl, headers=headers, data=data_json)
    resp_json = json.dumps(resp.json(), sort_keys=True, indent=4)
    return json.loads(resp_json)['purse'], json.loads(resp_json)['amountInPayCurrency']


async def invoice_one(invoice_id):
    request = '/api/v1/invoices/one'

    data = {
        "invoiceId": invoice_id,
        "orderId": "null",
        'nonce': nonce,
        'request': request

    }
    completeUrl = baseUrl + request
    data_json = json.dumps(data, separators=(',', ':'))
    payload = base64.b64encode(data_json.encode('ascii'))
    signature = hmac.new(secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()

    headers = {
        'Content-type': 'application/json',
        'X-EX-APIKEY': api_key,
        'X-EX-PAYLOAD': payload,
        'X-EX-SIGNATURE': signature,
    }
    resp = requests.post(completeUrl, headers=headers, data=data_json)
    resp_json = json.dumps(resp.json(), sort_keys=True, indent=4)
    return json.loads(resp_json)['statusName']


async def invoice_one_2(invoice_id):
    request = '/api/v1/invoices/one'

    data = {
        "invoiceId": invoice_id,
        "orderId": "null",
        'nonce': nonce,
        'request': request

    }
    completeUrl = baseUrl + request
    data_json = json.dumps(data, separators=(',', ':'))
    payload = base64.b64encode(data_json.encode('ascii'))
    signature = hmac.new(secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()

    headers = {
        'Content-type': 'application/json',
        'X-EX-APIKEY': api_key,
        'X-EX-PAYLOAD': payload,
        'X-EX-SIGNATURE': signature,
    }
    resp = requests.post(completeUrl, headers=headers, data=data_json)
    resp_json = json.dumps(resp.json(), sort_keys=True, indent=4)
    return json.loads(resp_json)['statusName'], \
        json.loads(resp_json)['purse'], \
        json.loads(resp_json)['payCurrency'], \
        json.loads(resp_json)['amountInPayCurrency']



