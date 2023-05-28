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
from api import Api

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


    # check if it its newsletter day
    if Api.send_or_not() == False:
        return

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
    EmailContent = create_email()

    # Create email
    for Email in EmailList:
        try:
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

# Create email
def create_email():
    header = '<!DOCTYPE html> <html> <head> <style> body { font-family: Arial, sans-serif; background-color: #f1f1f1; } .header { text-align: center; margin-bottom: 20px; } .logo { width: 200px; margin: 0 auto; } .content { background-color: #ffffff; padding: 20px; margin-bottom: 20px; } .headercontent{ background-color: red; padding: 0.5%; color: white; } </style> </head>'
    body = '<body> <div class="headercontent"> <div class="header"> <h1>Schweizer Nati Newsletter</h1> </div> </div> <div class="content"> <h2>Unsere Schweizer Nati spielt bald wieder!</h2> <img class="logo" src="https://upload.wikimedia.org/wikipedia/de/thumb/5/53/SFV_Logo.svg/1200px-SFV_Logo.svg.png" alt="Schweizer Nationalmannschaftslogo">'
    
    # Get Data from Api
    all_fixtures = Api.getGames()
    content = ""
    for fixture_info in all_fixtures:
        home_team = fixture_info[0].split(": ")[1]
        away_team = fixture_info[1].split(": ")[1]
        league_name = fixture_info[2].split(": ")[1]
        venue = fixture_info[3].split(": ")[1]
        date = fixture_info[4].split(": ")[1]

        # Check if Switzerland is the Home or Away Team
        if home_team != 'Switzerland':
            away_team = home_team
        
        # Access the away_team information
        content += f'<p style="font-size: 150%;">Datum: {date}</p>'
        content += f'<p style="font-size: 150%;">Gegner: {away_team}</p>'
        content += f'<p style="font-size: 150%;">Art: {league_name}</p>'
        content += f'<p style="font-size: 150%;">Ort: {venue}</p>'
        content += '<p style="font-size: 150%;"></p>'
    
    footer = "</div></body></html>"

    email_content = (header + body + content + footer)
    return email_content

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