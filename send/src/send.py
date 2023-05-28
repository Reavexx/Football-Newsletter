from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from email.message import EmailMessage
from email.mime.text import MIMEText
import google.auth

from db import Db

from datetime import date

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

import os

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
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        gmail_send_message(service)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

def gmail_send_message(service):
    # Get all emails from db
    EmailList = Db.getSubs()

    # Set email content 
    EmailContent = ""
    Header = "<h1>Hello</h1>"
    Body = ""
    Footer = "<h2>Goodbye</h2>"

    # Create email
    for Email in EmailList:
        try:

            EmailContent = (Header + Body + Footer)

            message = MIMEText(EmailContent, 'html')

            message['To'] = Email
            message['From'] = 'vroomvroomblitzer@gmail.com'
            message['Subject'] = 'Schwiizernati'

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # pylint: disable=E1101
            send_message = (service.users().messages().send
                            (userId="me", body=create_message).execute())
            print(F'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
    return send_message

# Log class
class Log:
    @staticmethod
    def error(message):
        with open('Newsletter_Volume/Sendlog.txt', 'a') as log_file:
            log_file.write("[ERROR] " + message + "\n")

    @staticmethod
    def info(message):
        print("[INFO] " + message)

if __name__ == '__main__':
    main()