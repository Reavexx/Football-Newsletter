from google.oauth2 import service_account
import googleapiclient.discovery
from googleapiclient.discovery import build

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

import base64
from email.message import EmailMessage
from email.mime.text import MIMEText
import google.auth

from db import Db

from datetime import date

import re

# Scopes required for accessing Gmail
SCOPES = ['https://mail.google.com/']

# Read environment variables from file
with open('/usr/app/src/Newsletter_Volume/envvar.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if line:
            key, value = line.split('=', 1)
            os.environ[key] = value

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # if os.path.exists('../../../send_docs/token.json'):
    #     creds = Credentials.from_authorized_user_file('../../../send_docs/token.json', SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             '../../../send_docs/credentials.json', SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open('../../../send_docs/token.json', 'w') as token:
    #         token.write(creds.to_json())

    if os.path.exists('Newsletter_Volume/token.json'):
        creds = Credentials.from_authorized_user_file('Newsletter_Volume/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Newsletter_Volume/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('Newsletter_Volume/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API to list messages
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', q='is:unread').execute()
        messages = results.get('messages', [])

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            # Get the email content (body or snippet)
            email_content = ''
            payload = msg.get('payload', {})
            parts = payload.get('parts', [])

            for part in parts:
                if part.get('body'):
                    # Get the text content of the part
                    data = part['body'].get('data')
                    if data:
                        # Decode and store the text content
                        email_content = base64.urlsafe_b64decode(data).decode('utf-8')
                        break

            # If email_content is still empty, fall back to snippet
            if not email_content:
                email_content = msg.get('snippet', '')

            headers = msg.get('payload', {}).get('headers', [])
            subject = ''
            sender = ''

            for header in headers:
                name = header['name'].lower()
                value = header['value']

                if name == 'subject':
                    subject = value
                elif name == 'from':
                    sender = value

            extracted_sender = extract_sender(sender)

            # Check if "STOP SENDING" is in the email content
            if 'STOP SENDING' in email_content:
                # Remove email from db
                Db.rmSub(extracted_sender)
                # Mark the email as read
                # mark_email_as_read(service, 'me', message['id'])
            
            # Check if "SIGN UP" is in the email content
            if 'SIGN UP' in email_content:
                # Add email to db
                Db.addSub(extracted_sender)

    except Exception as error:
        print(f"An error occurred: {error}")


def mark_email_as_read(service, user_id, message_id):
    try:
        # Mark the email as read
        message = service.users().messages().get(userId=user_id, id=message_id).execute()
        message['labelIds'] = [label for label in message['labelIds'] if label != 'UNREAD']
        service.users().messages().modify(userId=user_id, id=message_id, body=message).execute()
        print(f"Marked email {message_id} as read.")
    except HttpError as error:
        print(f"An error occurred while marking email {message_id} as read: {error}")

def extract_sender(string):
    # Extracts the email-adress from sender
    pattern = r'<([^<>]+)>'
    match = re.search(pattern, string)
    if match:
        content = match.group(1)
        return content
    else:
        return None

# Log class
class Log:
    @staticmethod
    def error(message):
        with open('Newsletter_Volume/Readlog.txt', 'a') as log_file:
            log_file.write("[ERROR] " + message + "\n")

    @staticmethod
    def info(message):
        print("[INFO] " + message)

if __name__ == '__main__':
    main()