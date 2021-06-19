#!/usr/bin/env python3.10


from __future__ import print_function

import datetime


# we need to change the import directory

# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# import google # auth.transport.requests.Request
# import googleapiclient # discovery.build
# import google_auth_oauthlib # flow.InstalledAppFlow

# from termcolor import colored

import json
import os
import pickle

import pathlib
import shutil

DEFAULT_GLOBAL_SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleEventHandler():
    def __init__(self):
        self.ensure_root()
        self.credentials = self.generate_credentials()
        self.service = googleapiclient.build(
            'calendar', 'v3', credentials=self.generate_credentials())
        if(not self.credentials or not self.service):
            raise ValueError('credentials or service has spoiled')

    def ensure_root(self):
        if(os.getuid() != 0):
            raise PermissionError('please run this as root')

    def generate_credentials(self):
        """
        GOAL: generate credentials for a specific Google account.
        This will be used to add events to a calendar
        """

        token_path = pathlib.Path(
            "/etc/StarbucksAutoma/credentials/token.pickle"
        )
        credentials_path = pathlib.Path(
            "/etc/StarbucksAutoma/credentials/credentials.json"
        )
        credentials = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                credentials = pickle.load(token)
            if(not credentials or not credentials.valid):
                if(credentials and credentials.expired and credentials.refresh_token):
                    credentials.refresh(Request())
        else:
            if not(os.path.exists(credentials_path)):
                shutil.copyfile("/tmp/credentials.json", credentials_path)
            application_flow = flow.InstalledAppFlow.from_client_secrets_file(
                credentials_path, DEFAULT_GLOBAL_SCOPES)
            credentials = application_flow.run_local_server()
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)
        return credentials

    def get_current_week(self) -> list[datetime.datetime]:
        """
        Get the current week's days in datetime.datetime objects.
        """

        week, counter = [], 0
        today = datetime.date.today()

        while(today.weekday() != 0):
            counter += 1
            today -= datetime.timedelta(days=1)
            week.append(today)

        today += datetime.timedelta(days=counter)
        for _ in range(counter, 7):
            week.append(today)
            today += datetime.timedelta(days=1)
        week.sort()
        return week

    def get_event_span(self, current: datetime.datetime):
        """
        Get a list of events that occur from the current time until
        the same time the next day
        This allows us to find events that need to be updated if there is a shift change occuring in the
        same day as `current`
        """

        if not(isinstance(current, datetime.datetime)):
            raise ValueError(
                f'expected datetime.datetime, received: {type(current).__name__}')
        next_day = f'{(current + datetime.timedelta(days=1)).isoformat()}Z'
        current = f'{current.isoformat()}Z'
        query = self.service.events().(calendarId='primary', timeMin=current,
                                       timeMax=next_day, maxResults=50, singleEvents=True, orderBy='startTime').execute()
        return query.get('items', [])
