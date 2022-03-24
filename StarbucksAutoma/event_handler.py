# Copyright 2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# http://www.apache.org/licenses/LICENSE-2.0
# You may obtain a copy of the License at
#
# distributed under the License is distributed on an "AS IS" BASIS,
# Unless required by applicable law or agreed to in writing, software
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Sources

checking if event is already in the calendar
   * https://stackoverflow.com/questions/55272913/how-to-check-google-calendar-to-see-if-event-already-exists-before-adding

using the freebusy API call
   * https://gist.github.com/cwurld/9b4e10dbeecab28345a3
"""


from __future__ import print_function

from StarbucksAutoma import event_packet
from StarbucksAutoma.exceptions import CrendentialFailure
from StarbucksAutoma.constants import TOKEN_PATH, CREDENTIALS_PATH, TOKEN_JSON_PATH

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from termcolor import colored

from types import NotImplementedType
import typing
import abc

import json
import os.path
import pickle

import pathlib
import shutil
import datetime

# If modifying these scopes, delete the file token.pickle.

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class EventHandler(abc.ABC):
    """Abstract base class for all calendar event handlers"""

    @abc.abstractmethod
    def generate_credentials(self):
        """Generate credentials to use this event handler"""

    @staticmethod
    def get_current_week() -> typing.List[datetime.datetime]:
        """Obtain a list of datetime objects representing the week we are in"""
        week, counter = [], 0
        today = datetime.date.today()

        while today.weekday() != 0:
            counter += 1
            today -= datetime.timedelta(days=1)
            week.append(today)

        today += datetime.timedelta(days=counter)

        for _ in range(counter, 7):
            week.append(today)
            today += datetime.timedelta(days=1)

        return sorted(week)

    @abc.abstractmethod
    def add_event(self, event: event_packet.EventPacket):
        """Append an event to the calendar"""

    @abc.abstractmethod
    def remove_event(self, event: event_packet.EventPacket):
        """Remove an event from the calendar"""

    @abc.abstractmethod
    def get_events_from_day(self, date: datetime.datetime) -> typing.Any:
        """Get all the events from a given day"""


class GoogleEventHandler(EventHandler):
    """Google Calendar event handler implementation"""

    def __init__(self):
        self.credentials = self.generate_credentials()
        print(self.credentials)
        self.service = build("calendar", "v3", credentials=self.credentials)

        print(self.service)

        # if not self.credentials or self.service:
        # raise CrendentialFailure("could not instaniate credentials")

    def generate_credentials(self):
        """Generate credentials for Google account and will be used to add events"""
        credentials = None

        """
        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first time.
        """

        if TOKEN_JSON_PATH.is_file():
            # if os.path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file(TOKEN_JSON_PATH, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                # flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)

                # credentials = flow.run_local_server(port=0)
                credentials.refresh(Request())
            else:

                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                # flow = InstalledAppFlow.from_client_secrets_file(
                # '/home/jared/Downloads/client_secret_815316007427-4a02hc9emrteh5t55i5tia1j07c6io73.apps.googleusercontent.com.json', SCOPES)
                credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(TOKEN_JSON_PATH, "w", encoding="utf-8") as token:
                token.write(credentials.to_json())

        return credentials

    def get_events_from_day(self, date: datetime.datetime) -> typing.List:
        current, next_ = map(
            lambda x: x.isoformat(), (date, date + datetime.timedelta(days=1))
        )
        return (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=current,
                timeMax=next_,
                maxResults=50,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
            .get("items", [])
        )

    def remove_event(self, event: str) -> None:
        """TODO: Check if event is present to even remove and report if not found"""

        self.service.events().delete(calendarId="primary", eventId=event).execute()

    def add_event(self, event: event_packet.EventPacket):
        """TODO: Check if event is present and update if needed"""

        self.service.events().insert(
            calendarId="primary", body=event.form_submit_body()
        ).execute()

        print(colored(f"Successfully added event {event}", "green"))
