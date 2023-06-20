import requests

url = 'http://109.172.81.133:3000/'
body = {
    "address": "TWB8NUDqB8rmvqds3aqyh7TpfELk5RL94u",
    "id": 3,
    "inviterId": 56
}

response = requests.post(url, json=body)

if response.status_code == 200:
    response_data = response.json()
    print(response_data)
else:
    print(f"Ошибка при отправке запроса: {response.status_code}")
    