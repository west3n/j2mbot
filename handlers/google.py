import base64
import datetime

import decouple
import gspread

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from oauth2client.service_account import ServiceAccountCredentials


async def sheets_connection():
    sheet_url = decouple.config("SHEET_URL")
    credentials_path = "handlers/j2m-project.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(sheet_url)
    return sh


async def send_email_message(to: str, subject: str, message_text: str):
    user_id = 'me'
    service = build('gmail', 'v1', credentials=Credentials(
        None,
        refresh_token=decouple.config('REFRESH_TOKEN'),
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=decouple.config('CLIENT_ID'),
        client_secret=decouple.config('CLIENT_SECRET')
    ))
    message = create_message(user_id, to, subject, message_text)
    sent_message = await send_message(service, user_id, message)
    if sent_message:
        print('Сообщение успешно отправлено!')
    else:
        print('Ошибка при отправке сообщения.')


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


async def send_message(service, user_id, message):
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        return sent_message
    except Exception as e:
        print(e)


async def add_new_transfer_data(tg_id, amount):
    sh = await sheets_connection()
    worksheet = sh.worksheet("Сумма пополнения пула")
    worksheet.append_row((datetime.datetime.now().date().strftime("%d.%m.%Y"),
                          tg_id, "Трансфер", amount, "Перевод из медиа в коллективный"))
