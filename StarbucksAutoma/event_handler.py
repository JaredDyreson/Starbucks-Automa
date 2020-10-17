#!/usr/bin/env python3.8

#
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

checking if event is already in the calendar --> https://stackoverflow.com/questions/55272913/how-to-check-google-calendar-to-see-if-event-already-exists-before-adding
also was a good idea to abstract this to a class ^ 
using the freebusy API call --> https://gist.github.com/cwurld/9b4e10dbeecab28345a3

"""


from __future__ import print_function
from StarbucksAutoma import event_packet

from datetime import datetime, timedelta, date

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from termcolor import colored

import json
import os.path
import pickle

import pathlib
import shutil

# If modifying these scopes, delete the file token.pickle.

SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleEventHandler():
    def __init__(self):
        self.ensure_root()
        self.credentials = self.gen_credentials()
        self.service = build('calendar', 'v3', credentials=self.gen_credentials())
        if (isinstance(self.credentials, type(None)) or
               isinstance(self.service, type(None))):
               raise ValueError

    def ensure_root(self):
        if(os.getuid() != 0):
            raise PermissionError("Run this class a root")

    def gen_credentials(self):
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
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
        else:
            if not(os.path.exists(credentials_path)):
                shutil.copyfile("/tmp/credentials.json", credentials_path)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            credentials = flow.run_local_server()
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)
        return credentials
    
    def get_current_week(self) -> list:
        """
        Get the current week's days into isoformat.
        """

        week, counter = [], 0
        today = date.today()

        while(today.weekday() != 0):
            counter += 1
            today -= timedelta(days=1)
            week.append(today)

        today += timedelta(days=counter)
        for _ in range(counter, 7):
            week.append(today)
            today += timedelta(days=1)
        week.sort()
        return week

    def get_event_day(self, current: datetime) -> list:
        next_day = '{}Z'.format((current+timedelta(days=1)).isoformat())
        current = '{}Z'.format(current.isoformat())
        return self.service.events().list(calendarId='primary', timeMin=current, 
                timeMax=next_day, maxResults=50, singleEvents=True, orderBy='startTime').execute().get('items', [])

    def generate_packet(self, raw_data) -> dict:
        return {
            'summary': raw_data["summary"],
            'start': raw_data['start']['dateTime'],
            'end': raw_data['end']['dateTime'],
            'event_id': raw_data['id']
        }

    def get_event_week(self, summary: str):
        work_week = []
        for day in get_current_week():
            response = get_event_day(day)
            for element in self.get_event_day(day):
                if(summary == element["summary"]):
                    packet = self.generate_packet(element)
                    work_week.append(packet)
        return work_week

    def remove_event(self, event_id: str) -> None:
        """
        Remove an event based on it's ID
        """

        if not(isinstance(event_id, str)):
            raise ValueError
        event_handler.service.events().delete(calendarId='primary', eventId=event_id).execute()

    def clear_work_week(self) -> None:
        """
        Clear an entire work week in one go
        """

        for element in self.get_event_week(event_name): 
            self.remove_event(element['id'])

    def check_event_presence(self, day: datetime, summary: str):
        """
        See if an event is already in the calendar
        """

        overlap_ = []
        for element in self.get_event_day(day):
            if(element['summary'] == summary): 
                packet = self.generate_packet(element)
                overlap_.append(packet)

        if(len(overlap_) == 0): 
            return (None, None, None, False)
        elif(len(overlap_) > 1): 
            return (overlap_[-1]['start'], overlap_[-1]['end'], overlap_[-1]['event_id'], True)
        return (overlap_[0]['start'], overlap_[0]['end'], overlap_[0]['event_id'] , True)


    def add_events(self, event: event_packet) -> None:
        """
        Add an event packet to the Google calendar API
        """

        # if not(isinstance(event, event_packet)):
            # raise ValueError

        start, end, event_id, status = self.check_event_presence(event.begin, event.summary)
        original_ = None

        if(start is None and end is None):
            json_complient_event = json.loads(event.form_submit_body())
            self.service.events().insert(calendarId='primary', body=json_complient_event).execute()
            success_message_ = "[+] Sucessfully added event {}".format(event.google_date_added_string())
            print(colored(success_message_, 'green', 'on_grey'))
        else:
            original_ = event_packet.event_packet.from_string(start, end, event.summary)
        if (original_ is not None):
            if not(original_ == event):
                json_complient_event = json.loads(event.form_submit_body())
                self.service.events().insert(calendarId='primary', body=json_complient_event).execute()
                self.service.events().delete(calendarId='primary', eventId=event_id).execute()
                success_message_ = "[+] Sucessfully updated event to {} from {}".format(
                      ' '.join(event.google_date_added_string().split()[1:]),
                      ' '.join(original_.google_date_added_string().split()[1:])
                )
                print(colored(success_message_, 'green', 'on_grey'))
        else:
            duplicate_event_message_ = "[-] Event {} is already in the calendar".format(event.google_date_added_string())
            print(colored(duplicate_event_message_, 'red', 'on_grey'))
