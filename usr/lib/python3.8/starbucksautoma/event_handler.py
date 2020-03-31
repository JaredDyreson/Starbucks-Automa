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

# NOTES

# [START calendar_quickstart], hacked with love -> Jay


# checking if event is already in the calendar --> https://stackoverflow.com/questions/55272913/how-to-check-google-calendar-to-see-if-event-already-exists-before-adding
# also was a good idea to abstract this to a class ^ 
# using the freebusy API call --> https://gist.github.com/cwurld/9b4e10dbeecab28345a3


from __future__ import print_function
from datetime import datetime
import pickle
from googleapiclient.discovery import build
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from pprint import pprint as pp
import getpass
from starbucksautoma import time_struct as ts
import re
from datetime import timedelta, date
from starbucksautoma import time_struct

from starbucksautoma import json_parser as jp
from termcolor import colored
# If modifying these scopes, delete the file token.pickle.

SCOPES = ['https://www.googleapis.com/auth/calendar']
parser = jp.jsonparser("/home/jared/Applications/starbucks_automa/credentials/config.json")

class GoogleEventHandler():
  def __init__(self):
    self.credentials = self.gen_credentials()
    self.service = build('calendar', 'v3', credentials=self.gen_credentials())
  def gen_credentials(self):
    location = str("/home/{}/Applications/starbucks_automa/credentials".format(getpass.getuser())) 
    credentials = None
    if os.path.exists('{}/token.pickle'.format(location)):
      with open('{}/token.pickle'.format(location), 'rb') as token:
        credentials = pickle.load(token)
      if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
          credentials.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('{}/credentials.json'.format(location), SCOPES)
      credentials = flow.run_local_server()
    with open('{}/token.pickle'.format(location), 'wb') as token:
      pickle.dump(credentials, token)
    return credentials
    
  def get_current_week(self) -> list:
    """
    Get the current week's days into isoformat.
    """
    week = []
    counter = 0
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    # wind the week day back 
    while(today.weekday() != 0):
      counter+=1
      today = today - timedelta(days=1)
      week.append(today)
    # advance date to current
    today+=timedelta(days=counter)
    # get the rest of the days
    for x in range(counter, 7):
      week.append(today)
      today+=timedelta(days=1)
    return week

  def get_event_day(self, current: datetime):
      next_day = '{}Z'.format((current+timedelta(days=1)).isoformat())
      current = '{}Z'.format(current.isoformat())
      return self.service.events().list(calendarId='primary', timeMin=current, timeMax=next_day, maxResults=50, singleEvents=True, orderBy='startTime').execute().get('items', [])

  def get_event_week(self, summary: str):
      work_week = []
      for day in get_current_week():
        response = get_event_day(day)
        for i, element in enumerate(response):
          summary_ = element['summary']
          if(summary == summary_):
            work_day = {
              'summary': summary,
              'start': element['start']['dateTime'],
              'end': element['end']['dateTime'],
              'event_id': element['id']
            }
            work_week.append(work_day)
      return work_week

  def remove_event(self, event_id: str) -> None:
      try: event_handler.service.events().delete(calendarId='primary', eventId=event_id).execute()
      except Exception as error: print("got an error: {}".format(error))

  def clear_work_week(self) -> None:
      for element in self.get_event_week(event_name): self.remove_event(element['id'])

  def check_event_presence(self, day: datetime, summary: str):
      day_events = self.get_event_day(day)
      overlap_ = []
      for element in day_events:
        if(element['summary'] == summary): 
            work_day = {
              'summary': summary,
              'start': element['start']['dateTime'],
              'end': element['end']['dateTime'],
              'event_id': element['id']
            }
            overlap_.append(work_day)
      if(len(overlap_) == 0): return None, None, None, False
      elif(len(overlap_) > 1): return overlap_[-1]['start'], overlap_[-1]['end'], overlap_[-1]['event_id'], True
      return overlap_[0]['start'], overlap_[0]['end'], overlap_[0]['event_id'] , True


  def add_events(self, event: time_struct) -> None:
    start, end, event_id, status = self.check_event_presence(event.begin, event.summary)
    if(start is None and end is None):
      json_complient_event = json.loads(event.form_submit_body())
      self.service.events().insert(calendarId='primary', body=json_complient_event).execute()
      success_message_ = "[+] Sucessfully added event {}".format(event.google_date_added_string())
      print(colored(success_message_, 'green', 'on_grey'))
    else:
      original_ = ts.time_struct.from_string(start, end, event.summary)
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
