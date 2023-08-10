import base64
import decouple
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText


async def sheets_connection():
    sheet_url = decouple.config("SHEET_URL")
    credentials_path = "../j2m-project-395212-6143ef593cd0.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(sheet_url)
    return sh


async def send_email_message(to: str, subject: str, message_text: str):
    print(to)
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
